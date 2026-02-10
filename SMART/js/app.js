// API Functions
const API = {
    async getMedicines() {
        const { data, error } = await supabaseClient
            .from('medicines')
            .select('*')
            .order('name');
        return { data, error };
    },

    async getProcedures() {
        const { data, error } = await supabaseClient
            .from('procedures')
            .select('*')
            .order('name');
        return { data, error };
    },

    async searchItem(query, type) {
        const table = type === 'medicine' ? 'medicines' : 'procedures';
        const { data, error } = await supabaseClient
            .from(table)
            .select('*')
            .ilike('name', `%${query}%`)
            .limit(10);
        return { data, error };
    },

    async saveBill(billData) {
        const { data, error } = await supabaseClient
            .from('bills')
            .insert([billData])
            .select();
        return { data, error };
    },

    async saveBillItems(items) {
        const { data, error } = await supabaseClient
            .from('bill_items')
            .insert(items);
        return { data, error };
    },

    async getBills() {
        const { data, error } = await supabaseClient
            .from('bills')
            .select('*')
            .order('created_at', { ascending: false });
        return { data, error };
    },

    async saveQuickCheck(itemName, itemType, chargedPrice, isValid, overcharge) {
        const billData = {
            patient_name: 'Quick Check',
            hospital_name: 'Price Verification',
            bill_date: new Date().toISOString().split('T')[0],
            total_amount: chargedPrice,
            verified: true,
            overcharged: !isValid
        };
        const { data, error } = await supabaseClient
            .from('bills')
            .insert([billData])
            .select();
        return { data, error };
    },

    async saveComplaint(complaintData) {
        const { data, error } = await supabaseClient
            .from('complaints')
            .insert([complaintData])
            .select();
        return { data, error };
    },

    async getComplaints() {
        const { data, error } = await supabaseClient
            .from('complaints')
            .select('*')
            .order('created_at', { ascending: false });
        return { data, error };
    },

    async getStats() {
        const { data: bills } = await supabaseClient.from('bills').select('*');
        const { data: complaints } = await supabaseClient.from('complaints').select('*');
        
        const total = bills?.length || 0;
        const overcharged = bills?.filter(b => b.overcharged).length || 0;
        const totalComplaints = complaints?.length || 0;
        
        return {
            data: {
                total_bills: total,
                overcharged_bills: overcharged,
                valid_bills: total - overcharged,
                total_complaints: totalComplaints
            },
            error: null
        };
    }
};

// Utility Functions
const Utils = {
    formatCurrency(amount) {
        return `₹${parseFloat(amount).toFixed(2)}`;
    },

    validatePrice(charged, minPrice, maxPrice) {
        return charged >= minPrice && charged <= maxPrice;
    },

    calculateOvercharge(charged, maxPrice) {
        return charged > maxPrice ? charged - maxPrice : 0;
    },

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => alertDiv.remove(), 5000);
    }
};

// Price Checker
class PriceChecker {
    constructor() {
        this.results = [];
    }

    async checkPrice(itemName, itemType, chargedPrice, saveToDb = false) {
        const { data, error } = await API.searchItem(itemName, itemType);
        
        if (error || !data || data.length === 0) {
            return { found: false, message: 'Item not found in government database' };
        }

        const item = data[0];
        const isValid = Utils.validatePrice(chargedPrice, item.govt_min_price, item.govt_max_price);
        const overcharge = Utils.calculateOvercharge(chargedPrice, item.govt_max_price);

        if (saveToDb) {
            await API.saveQuickCheck(itemName, itemType, chargedPrice, isValid, overcharge);
        }

        return {
            found: true,
            item: item,
            chargedPrice: chargedPrice,
            isValid: isValid,
            overcharge: overcharge,
            message: isValid ? 'Price is within government limits' : `Overcharged by ${Utils.formatCurrency(overcharge)}`
        };
    }

    displayResult(result, container) {
        if (!result.found) {
            container.innerHTML = `<div class="alert alert-warning">${result.message}</div>`;
            return;
        }

        const resultHTML = `
            <div class="result-card ${result.isValid ? 'valid' : 'overcharged'}">
                <h3>${result.item.name}</h3>
                <p><strong>Category:</strong> ${result.item.category}</p>
                <div class="price-comparison">
                    <div class="price-item">
                        <label>Charged Price</label>
                        <div class="price ${result.isValid ? 'valid' : 'invalid'}">
                            ${Utils.formatCurrency(result.chargedPrice)}
                        </div>
                    </div>
                    <div class="price-item">
                        <label>Govt Min Price</label>
                        <div class="price">${Utils.formatCurrency(result.item.govt_min_price)}</div>
                    </div>
                    <div class="price-item">
                        <label>Govt Max Price</label>
                        <div class="price">${Utils.formatCurrency(result.item.govt_max_price)}</div>
                    </div>
                </div>
                <div style="margin-top: 1rem;">
                    <span class="badge ${result.isValid ? 'badge-success' : 'badge-danger'}">
                        ${result.message}
                    </span>
                </div>
            </div>
        `;
        
        container.innerHTML = resultHTML;
    }
}

// Bill Verifier
class BillVerifier {
    constructor() {
        this.billItems = [];
    }

    addItem(item) {
        this.billItems.push(item);
    }

    clearItems() {
        this.billItems = [];
    }

    async verifyBill() {
        const results = [];
        let totalOvercharge = 0;
        let hasOvercharge = false;

        for (const item of this.billItems) {
            const result = await new PriceChecker().checkPrice(
                item.name,
                item.type,
                item.price
            );
            
            if (result.found) {
                results.push({
                    ...item,
                    ...result
                });
                
                if (!result.isValid) {
                    hasOvercharge = true;
                    totalOvercharge += result.overcharge;
                }
            }
        }

        return {
            items: results,
            totalOvercharge: totalOvercharge,
            hasOvercharge: hasOvercharge,
            verified: true
        };
    }

    async saveBill(patientName, hospitalName, billDate) {
        const verification = await this.verifyBill();
        const totalAmount = this.billItems.reduce((sum, item) => sum + parseFloat(item.price), 0);

        const billData = {
            patient_name: patientName,
            hospital_name: hospitalName,
            bill_date: billDate,
            total_amount: totalAmount,
            verified: true,
            overcharged: verification.hasOvercharge
        };

        const { data: billRecord, error: billError } = await API.saveBill(billData);
        
        if (billError) {
            throw new Error('Failed to save bill');
        }

        const billItems = verification.items.map(item => ({
            bill_id: billRecord[0].id,
            item_type: item.type,
            item_id: item.item.id,
            item_name: item.item.name,
            charged_price: item.chargedPrice,
            govt_max_price: item.item.govt_max_price,
            is_overcharged: !item.isValid
        }));

        await API.saveBillItems(billItems);

        return {
            success: true,
            billId: billRecord[0].id,
            verification: verification
        };
    }

    displayVerification(verification, container) {
        let html = '<div class="card"><h3>Bill Verification Results</h3>';
        
        verification.items.forEach(item => {
            html += `
                <div class="result-card ${item.isValid ? 'valid' : 'overcharged'}">
                    <h4>${item.name}</h4>
                    <div class="price-comparison">
                        <div class="price-item">
                            <label>Charged</label>
                            <div class="price ${item.isValid ? 'valid' : 'invalid'}">
                                ${Utils.formatCurrency(item.chargedPrice)}
                            </div>
                        </div>
                        <div class="price-item">
                            <label>Max Allowed</label>
                            <div class="price">${Utils.formatCurrency(item.item.govt_max_price)}</div>
                        </div>
                    </div>
                    <span class="badge ${item.isValid ? 'badge-success' : 'badge-danger'}">
                        ${item.message}
                    </span>
                </div>
            `;
        });

        if (verification.hasOvercharge) {
            html += `
                <div class="alert alert-danger">
                    <strong>Total Overcharge: ${Utils.formatCurrency(verification.totalOvercharge)}</strong>
                </div>
            `;
        } else {
            html += `<div class="alert alert-success">All prices are within government limits!</div>`;
        }

        html += '</div>';
        container.innerHTML = html;
    }
}
