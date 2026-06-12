// --- UNIFIED CUSTOM CURSOR LOGIC ---
document.addEventListener('mousemove', (e) => {
    const cursor = document.getElementById('c-cursor');
    const follower = document.getElementById('c-follower');
    if(cursor && follower) {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        follower.style.left = (e.clientX - (follower.offsetWidth/2)) + 'px';
        follower.style.top = (e.clientY - (follower.offsetHeight/2)) + 'px';
    }
});

// --- USER DASHBOARD LOGIC ---
let currentMethod = 'upi';

document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.flash-msg');
    messages.forEach(function(msg) {
        setTimeout(function() {
            msg.classList.add('fade-out');
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});

function openProfile() { const p = document.getElementById('profileModal'); if(p) p.classList.add('active'); }
function closeProfile() { const p = document.getElementById('profileModal'); if(p) p.classList.remove('active'); }

function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) { document.getElementById('profile-preview').src = e.target.result; }
        reader.readAsDataURL(input.files[0]);
    }
}

async function reverseRow(event, btn, txId) {
    event.stopPropagation();
    if(confirm("Reverse this transaction? This creates an immutable reversal record in the blockchain.")) {
        try {
            const response = await fetch(`/reverse_transaction/${txId}`, { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' } 
            });
            const data = await response.json();
            if(data.success) {
                alert(data.message);
                window.location.reload(); // Refresh to update blockchain state
            } else { alert(data.message); }
        } catch (err) { alert("Reversal request failed!"); }
    }
}

function openReceipt(amount, method, recipient, time) {
    const mAmount = document.getElementById('modal-amount');
    if(mAmount) {
        mAmount.innerText = parseFloat(amount).toLocaleString(undefined, {minimumFractionDigits: 2});
        document.getElementById('modal-method').innerText = method;
        document.getElementById('modal-recipient').innerText = recipient;
        document.getElementById('modal-time').innerText = time;
        document.getElementById('receiptModal').classList.add('active');
    }
}

function closeReceipt() { const r = document.getElementById('receiptModal'); if(r) r.classList.remove('active'); }

function setMethod(method) {
    currentMethod = method;
    document.querySelectorAll('.method-btn').forEach(btn => btn.classList.remove('active-tab'));
    const activeBtn = document.getElementById('tab-' + method);
    if(activeBtn) activeBtn.classList.add('active-tab');
    
    const label = document.getElementById('method-label');
    const input = document.getElementById('recipient-id');
    if(!label || !input) return;

    if(method === 'upi') { label.innerText = 'UPI ID / Account No'; input.placeholder = 'CBL-XXXXXX'; } 
    else if(method === 'paypal') { label.innerText = 'PayPal Email'; input.placeholder = 'Enter email address'; } 
    else { label.innerText = 'MFS Number (bKash/Nagad)'; input.placeholder = '01XXXXXXXXX'; }
}

async function confirmTransfer() {
    const amountInput = document.getElementById('transfer-amount');
    const recipientInput = document.getElementById('recipient-id');
    if(!amountInput || !recipientInput) return;

    const amount = amountInput.value;
    const recipient = recipientInput.value;
    if(!amount || !recipient) { alert("Please complete all fields."); return; }
    
    try {
        const response = await fetch('/transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, recipient, method: currentMethod })
        });
        const data = await response.json();
        
        if(data.success) {
            document.getElementById('display-balance').innerText = data.new_balance;
            const box = document.getElementById('statement-box');
            if(box) {
                const row = document.createElement('div');
                const now = new Date().toLocaleString();
                row.onclick = () => openReceipt(amount, currentMethod, data.recipient_name, now);
                row.className = "group flex justify-between items-center p-4 bg-red-50 rounded-2xl border border-red-100 animate-pulse mb-3 cursor-pointer transition-all active:scale-95";
                row.innerHTML = `
                    <div class="flex items-center">
                        <div class="w-9 h-9 bg-white text-red-500 rounded-xl flex items-center justify-center mr-3 shadow-sm"><i class="fas fa-arrow-up text-[10px]"></i></div>
                        <div><p class="font-bold text-slate-800 text-xs">${currentMethod.toUpperCase()} Sent</p><p class="text-[9px] text-slate-400 font-bold uppercase">To: ${data.recipient_name}</p></div>
                    </div>
                    <div class="flex items-center gap-3">
                        <p class="font-black text-red-500 text-xs">-৳ ${parseFloat(amount).toLocaleString()}</p>
                        <button onclick="reverseRow(event, this, '${data.tx_id}')" title="Reverse Transaction" class="text-slate-300 hover:text-blue-500 transition-colors px-2 py-1"><i class="fas fa-undo-alt text-[10px]"></i></button>
                    </div>`;
                box.prepend(row);
                setTimeout(() => row.classList.remove('animate-pulse'), 1000);
            }
            amountInput.value = ""; recipientInput.value = "";

            const flashContainer = document.getElementById('flash-messages-container');
            if(flashContainer) {
                const newFlash = document.createElement('div');
                newFlash.className = "flash-msg mb-4 p-4 rounded-2xl text-[11px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-600 border border-emerald-100";
                newFlash.innerHTML = `<i class="fas fa-check-circle mr-2"></i> ${data.message}`;
                flashContainer.appendChild(newFlash);
                setTimeout(() => { newFlash.classList.add('fade-out'); setTimeout(() => newFlash.remove(), 500); }, 5000);
            }
        } else { alert(data.message); }
    } catch (err) { alert("Connection error!"); }
}

// --- HOME PAGE LOGIC (POPUP & CAROUSEL) ---
const contentData = {
    'Personal': { title: 'Premium Personal Banking', icon: 'fa-user-circle', text: 'Experience the pinnacle of lifestyle banking. Our personal accounts offer seamless global transactions, high-yield interest rates, and a dedicated wealth manager to guide your financial journey.' },
    'Business': { title: 'Corporate Financial Solutions', icon: 'fa-briefcase', text: 'Empower your enterprise with our robust business suite. From automated payroll systems to international trade finance, we provide the tools necessary for global expansion and fiscal efficiency.' },
    'SME': { title: 'Empowering Small Businesses', icon: 'fa-rocket', text: 'Chittagong Bank is dedicated to fueling the growth of SMEs. Access collateral-free loans, digital payment gateways, and expert consultancy designed to scale your startup into a market leader.' },
    'Agent': { title: 'Inclusion through Agent Banking', icon: 'fa-handshake', text: 'Bridging the gap between traditional banking and the unbanked. Our agent banking network ensures that professional financial services are accessible even in the most remote corners of the nation.' },
    'Digital': { title: 'The Digital Ecosystem', icon: 'fa-microchip', text: 'Our AI-driven digital platform provides real-time spending insights, biometric security, and 24/7 instant fund transfers across international borders with zero friction.' },
    'Retail Accounts': { title: 'High-Performance Savings', icon: 'fa-wallet', text: 'Open a Retail Account and enjoy instant liquidity with maximum security. Benefit from our tiered interest rates and zero-maintenance fee policy for active users.' },
    'Business Accounts': { title: 'Dynamic Asset Management', icon: 'fa-building-columns', text: 'Manage your corporate capital with precision. Our business accounts integrate directly with ERP systems, allowing for real-time auditing and financial oversight.' },
    'Credit Cards': { title: 'World Elite Mastercard', icon: 'fa-credit-card', text: 'Unleash global privileges with our premium credit cards. Enjoy airport lounge access, 5% cashback on international travel, and comprehensive fraud protection.' },
    'Debit Cards': { title: 'Instant Global Access', icon: 'fa-money-check', text: 'Our Contactless Debit Cards are accepted at over 40 million outlets worldwide. Featuring EMV chip technology for the highest level of transaction security.' },
    'Home Loan': { title: 'Dream Home Financing', icon: 'fa-home', text: 'Secure your future with our competitive mortgage plans. We offer flexible repayment tenures up to 25 years with rapid approval processes and minimal documentation.' },
    'Auto Loan': { title: 'Luxury Vehicle Financing', icon: 'fa-car', text: 'Drive your ambition with our Auto Loan schemes. Offering up to 90% financing on both new and reconditioned vehicles with attractive interest rates.' },
    'Fixed Deposit': { title: 'Guaranteed Wealth Growth', icon: 'fa-vault', text: 'Invest in our Fixed Deposit Schemes for high-yield, risk-free returns. Tailor your maturity periods from 3 months to 5 years to match your financial goals.' },
    'DPS Scheme': { title: 'Systematic Savings Plan', icon: 'fa-chart-line', text: 'Build your fortune one month at a time. Our Deposit Pension Scheme (DPS) offers compounded interest rates, ensuring a massive corpus for your retirement.' },
    'Security': { title: 'Tier-1 Security Protocol', icon: 'fa-shield-halved', text: 'We employ military-grade 256-bit AES encryption and multi-factor authentication (MFA) to ensure that your digital assets and personal data remain impenetrable.' },
    'Bonus': { title: 'Welcome to the Elite', icon: 'fa-gift', text: 'Join Chittagong Bank today and receive an instant ৳500 credit to your new account. It’s our way of saying welcome to the future of banking.' },
    'Loan Rates': { title: 'Market Leading Interest', icon: 'fa-percentage', text: 'Experience the lowest borrowing costs in the region. Our loan products start at just 7.5% APR, designed to make your financial dreams affordable.' },
    'Privacy': { title: 'Global Privacy Standard', icon: 'fa-eye-slash', text: 'Your privacy is our priority. We strictly adhere to GDPR and international data protection laws, ensuring your financial footprint is never shared with third parties.' }
};

function openSmartPopup(key) {
    const data = contentData[key] || { title: 'Information', icon: 'fa-info-circle', text: 'Detailed information will be updated soon.' };
    const modal = document.getElementById('smart-modal');
    const body = document.getElementById('modal-body');
    if(!modal || !body) return;

    body.innerHTML = `
        <div class="flex items-center gap-5 mb-4">
            <div class="w-16 h-16 bg-red-50 rounded-2xl flex items-center justify-center text-red-600 text-3xl">
                <i class="fas ${data.icon}"></i>
            </div>
            <div>
                <h2 class="text-2xl font-black text-[#002e5b] uppercase tracking-tighter">${data.title}</h2>
                <div class="h-1 w-12 bg-red-600 mt-1"></div>
            </div>
        </div>
        <p class="text-gray-600 font-medium leading-relaxed text-lg">${data.text}</p>
        <div class="pt-6 border-t border-gray-100 flex gap-4">
            <button onclick="closeModal()" class="px-8 py-3 bg-[#002e5b] text-white rounded-xl font-bold text-xs uppercase tracking-widest">Understood</button>
            <button onclick="window.location.href='/register'" class="px-8 py-3 border-2 border-red-600 text-red-600 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-red-600 hover:text-white transition-all">Apply Now</button>
        </div>
    `;
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('smart-modal');
    if(modal) modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

let state = ['pos-left-1', 'pos-center', 'pos-right-1'];
function moveCarousel(dir) {
    const slides = document.querySelectorAll('.slide-item');
    if(slides.length === 0) return;
    if (dir === 1) state.push(state.shift());
    else state.unshift(state.pop());
    slides.forEach((slide, i) => { slide.className = `slide-item ${state[i]}`; });
}

// Auto-run carousel & setup escape key if on Home Page
if(document.querySelector('.slider-wrapper')) {
    setInterval(() => moveCarousel(1), 6000);
    document.addEventListener('keydown', (e) => { if (e.key === "Escape") closeModal(); });
}

function switchTab(tab) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');

    if (!loginForm || !registerForm) return; 

    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        tabLogin.classList.add('text-[#005b9f]', 'border-b-2', 'border-[#005b9f]');
        tabLogin.classList.remove('text-gray-400');
        tabRegister.classList.add('text-gray-400');
        tabRegister.classList.remove('text-[#005b9f]', 'border-b-2', 'border-[#005b9f]');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        tabRegister.classList.add('text-[#005b9f]', 'border-b-2', 'border-[#005b9f]');
        tabRegister.classList.remove('text-gray-400');
        tabLogin.classList.add('text-gray-400');
        tabLogin.classList.remove('text-[#005b9f]', 'border-b-2', 'border-[#005b9f]');
    }
}