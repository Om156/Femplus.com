const els = id => document.getElementById(id);

function getBase(){
    try{
        const url = new URL(window.location.href);
        const apiParam = url.searchParams.get('api');
        if(apiParam){
            localStorage.setItem('API_BASE', apiParam);
            return apiParam;
        }
    }catch(_){/* noop */}
    const saved = localStorage.getItem('API_BASE');
    if(saved) return saved;
    if(location.protocol.startsWith('http')){
        return `http://localhost:8000`;
    }
    return 'http://localhost:8000';
}

function api(path){
    let base = getBase() || '';
    base = String(base).trim().replace(/["']/g, '').replace(/\/$/, '');
    const suffix = path.startsWith('/') ? path : `/${path}`;
    return `${base}${suffix}`;
}

function setStatus(id, msg, isError=false){
    const el = els(id);
    if(!el) return;
    el.textContent = msg;
    el.style.color = isError ? '#e74c3c' : '#9aa3c7';
}

function toast(message, type='ok'){
    const container = document.getElementById('toast-container');
    if(!container) return;
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = message;
    container.appendChild(t);
    setTimeout(() => {
        t.style.opacity = '0';
        t.style.transform = 'translateY(6px)';
        setTimeout(() => container.removeChild(t), 250);
    }, 2200);
}

function showLoader(){
    const l = document.getElementById('loader');
    if(l){ l.classList.remove('hidden'); }
}
function hideLoader(){
    const l = document.getElementById('loader');
    if(l){ l.classList.add('hidden'); }
}

async function withLoading(fn){
    try{ showLoader(); return await fn(); }
    finally{ hideLoader(); }
}

function initApp(){
    try { toast('UI loaded'); } catch(_) {}
    
    const savedEmail = localStorage.getItem('AUTH_EMAIL');
    const savedToken = localStorage.getItem('AUTH_TOKEN');
    
    if(savedEmail && savedToken){
        showLoggedInUI(savedEmail);
        toggleAuthTabs(false);
        setTabsForAuth(true);
        showDashboardSection();
        // Prefill analysis email with logged in user
        const analysisEmail = document.getElementById('analysis-email');
        if(analysisEmail) analysisEmail.value = savedEmail;
    } else {
        setTabsForAuth(false);
        showWelcomeSection();
    }

    // ######### TABS ##############
    const tabs = document.querySelectorAll('.tabbar .tab');
    const indicator = document.getElementById('tab-indicator');

    function moveIndicator(target){
        if(!indicator || !target) return;
        const rect = target.getBoundingClientRect();
        const parentRect = target.parentElement.getBoundingClientRect();
        indicator.style.left = (rect.left - parentRect.left) + 'px';
        indicator.style.width = rect.width + 'px';
    }

    function initIndicator(){
        const active = document.querySelector('.tab.active');
        moveIndicator(active);
    }
    window.addEventListener('resize', () => initIndicator());
    setTimeout(initIndicator, 100); // Increased timeout to ensure DOM is ready

///////////// Reveal on scroll /////////////
    const observer = new IntersectionObserver((entries)=>{
        entries.forEach(e=>{
            if(e.isIntersecting){ e.target.classList.add('in'); }
        });
    },{threshold:0.08});
    document.querySelectorAll('.card, .feature, .stat').forEach(el=>{
        el.classList.add('reveal');
        observer.observe(el);
    });

    tabs.forEach(btn => btn.addEventListener('click', (e) => {
        e.preventDefault();
        
        const targetId = btn.getAttribute('data-target');
        const isAuthed = !!localStorage.getItem('AUTH_TOKEN');
        const publicViews = new Set(['home-section','signup-section','login-section']);
        
        if(!isAuthed && !publicViews.has(targetId)){
            toast('Please login to access the dashboard','err');
            const loginTab = document.querySelector('[data-target="login-section"]');
            if(loginTab) loginTab.click();
            return;
        }

        // Remove active class from all tabs
        tabs.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Move indicator
        moveIndicator(btn);
        
        // Show/hide sections
        document.querySelectorAll('.view').forEach(sec => {
            if(sec.id === targetId){ 
                sec.classList.remove('hidden'); 
                sec.scrollIntoView({behavior:'smooth', block:'start'}); 
                // Prefill analysis email when analysis section is accessed
                if(targetId === 'analysis-section') {
                    prefillAnalysisEmail();
                }
            } else { 
                sec.classList.add('hidden'); 
            }
        });
        
        // Handle home-only elements
        document.querySelectorAll('.home-only').forEach(el => {
            if(targetId === 'home-section') {
                el.classList.remove('hidden');
            } else {
                el.classList.add('hidden');
            }
        });
    }));

    const see = document.getElementById('btn-see-features');
    if(see){ see.addEventListener('click', () => {
        //////// Go to Features tab //////
        const tab = Array.from(document.querySelectorAll('.tab')).find(t => t.getAttribute('data-target') === 'features-section');
        if(tab){ tab.click(); }
    }); }

    // Login: new user → signup
    const goSignup = document.getElementById('go-signup');
    if(goSignup){ goSignup.addEventListener('click', (e)=>{
        e.preventDefault();
        const t = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target==='signup-section');
        if(t) t.click();
    }); }

    // Home page flow handlers
    const btnNewUser = document.getElementById('btn-new-user');
    const btnExistingUser = document.getElementById('btn-existing-user');
    
    if(btnNewUser) {
        btnNewUser.addEventListener('click', () => {
            const signupTab = document.querySelector('[data-target="signup-section"]');
            if(signupTab) signupTab.click();
        });
    }
    
    if(btnExistingUser) {
        btnExistingUser.addEventListener('click', () => {
            const loginTab = document.querySelector('[data-target="login-section"]');
            if(loginTab) loginTab.click();
        });
    }

    // Social login handlers
    const googleSignup = document.getElementById('google-signup');
    const facebookSignup = document.getElementById('facebook-signup');
    const instagramSignup = document.getElementById('instagram-signup');
    
    if(googleSignup) {
        googleSignup.addEventListener('click', () => {
            toast('Google signup coming soon!', 'ok');
        });
    }
    
    if(facebookSignup) {
        facebookSignup.addEventListener('click', () => {
            toast('Facebook signup coming soon!', 'ok');
        });
    }
    
    if(instagramSignup) {
        instagramSignup.addEventListener('click', () => {
            toast('Instagram signup coming soon!', 'ok');
        });
    }

///////// Signup /////////////
    const signupForm = document.getElementById('signup-form');
    if(signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('signup-email').value.trim();
            const password = document.getElementById('signup-password').value;
            const password2 = document.getElementById('signup-password2').value;
            const termsChecked = document.getElementById('terms-check').checked;
            
            /////////// Basic Authentication and validation ////////
            if(!email || !password) {
                toast('Email and password are required', 'err');
                return;
            }
            if(password !== password2) {
                toast('Passwords do not match', 'err');
                return;
            }
            if(!termsChecked) {
                toast('Please agree to Terms & Conditions', 'err');
                return;
            }
            
            /////////// Show loading //////////
            const signupBtn = document.getElementById('signup-btn');
            const originalText = signupBtn.textContent;
            signupBtn.textContent = 'Signing up...';
            signupBtn.disabled = true;
            
            try {
                const response = await fetch(api('/auth/signup'), {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if(response.ok) {
                    toast('Signup successful! Please login.');
                    signupForm.reset();
                    /////////// Switch to login tab ///////////
                    const loginTab = document.querySelector('[data-target="login-section"]');
                    if(loginTab) loginTab.click();
                } else {
                    toast(data.detail || 'Signup failed', 'err');
                }
            } catch(error) {
                toast('Network error. Please try again.', 'err');
                console.error('Signup error:', error);
            } finally {
                ////////// Restore button ////////
                signupBtn.textContent = originalText;
                signupBtn.disabled = false;
            }
        });
    }


    ///////////// Auth: login ///////////
    const loginBtn = els('login-btn');
    if(loginBtn) {
        loginBtn.addEventListener('click', async () => {
            await withLoading(async () => {
                const emailEl = els('login-email');
                const passwordEl = els('login-password');
                if(!emailEl || !passwordEl) {
                    toast('Login form not found', 'err');
                    return;
                }
                const email = emailEl.value.trim();
                const password = passwordEl.value;
            try{
                const res = await fetch(api('/auth/login'),{
                    method:'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({email, password})
                });
                const data = await safeJson(res);
                els('login-result').textContent = JSON.stringify(data,null,2);
                if(data && data.access_token){
                    localStorage.setItem('AUTH_TOKEN', data.access_token);
                    localStorage.setItem('AUTH_EMAIL', email);
                    showLoggedInUI(email);
                    toggleAuthTabs(false);
                    setTabsForAuth(true);
                    showDashboardSection();
                    // Prefill analysis email with logged in user
                    const a = document.getElementById('analysis-email');
                    if(a) a.value = email;
                    ////////////// Land on Home dashboard after login ////////////////
                    const homeTab = document.querySelector('[data-target="home-section"]');
                    if(homeTab) homeTab.click();
                    toast('Logged in');
                } else {
                    toast(data.detail || 'Login failed','err');
                }
            }catch(e){ 
                const resultEl = els('login-result');
                if(resultEl) resultEl.textContent = String(e); 
                toast('Login error','err'); 
            }
        });
        });
    }

    //////////////// Add reading ////////////////
    const addReadingBtn = els('add-reading-btn');
    if(addReadingBtn) {
        addReadingBtn.addEventListener('click', async () => {
        // Require login to save
        if(!localStorage.getItem('AUTH_TOKEN')){
            toast('Please login to save readings','err');
            const t = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target==='login-section');
            if(t) t.click();
            return;
        }
        await withLoading(async () => {
            const payload = {
                user_email: els('reading-email').value.trim(),
                flow_ml: numOrNull(els('flow-ml').value),
                hb: numOrNull(els('hb').value),
                ph: numOrNull(els('ph').value),
                crp: numOrNull(els('crp').value),
                hba1c_ratio: numOrNull(els('hba1c').value),
                clots_score: numOrNull(els('clots').value),
                cycle_id: emptyToUndefined(els('cycle-id').value),
                fsh_level: numOrNull(els('fsh').value),
                lh_level: numOrNull(els('lh').value),
                amh_level: numOrNull(els('amh').value),
                tsh_level: numOrNull(els('tsh').value),
                prolactin_level: numOrNull(els('prolactin').value)
            };
            try{
                const headers = {'Content-Type':'application/json'};
                const b = bearer();
                if(b) headers['Authorization'] = b;
                const res = await fetch(api('/flow/single'),{
                    method:'POST', headers,
                    body: JSON.stringify(payload)
                });
                const data = await safeJson(res);
                els('add-reading-result').textContent = JSON.stringify(data,null,2);
                if(res.ok) toast('Reading added'); else toast('Add reading failed','err');
            }catch(e){ 
                const resultEl = els('add-reading-result');
                if(resultEl) resultEl.textContent = String(e); 
                toast('Network error','err'); 
            }
        });
        });
    }

    // Analysis
    const fetchAnalysisBtn = els('fetch-analysis-btn');
    if(fetchAnalysisBtn) {
        fetchAnalysisBtn.addEventListener('click', async () => {
        await withLoading(async () => {
            const email = els('analysis-email').value.trim();
            try{
                const res = await fetch(api(`/flow/analysis/${encodeURIComponent(email)}`));
                const data = await safeJson(res);
                renderRiskCards('analysis-result', data.flags || {}, 'analysis');
                if(res.ok) toast('Analysis loaded'); else toast('Failed to load analysis','err');
            }catch(e){ 
                const resultEl = els('analysis-result');
                if(resultEl) resultEl.textContent = String(e); 
                toast('Network error','err'); 
            }
        });
        });
    }

}

// Initialize app when DOM is ready
if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// Drawer and account menu only (AI assistant removed)
(function(){
    const ready = () => {
        const pbtn = document.getElementById('profile-btn');
        const profileMenu = document.getElementById('profile-menu');
        const drawer = document.getElementById('profile-drawer');
        const backdrop = document.getElementById('profile-backdrop');
        const drawerClose = document.getElementById('drawer-close');

        function openDrawer(){
            if(drawer){
                drawer.classList.remove('hidden');
                drawer.setAttribute('aria-hidden','false');
                setTimeout(()=>drawer.classList.add('open'),0);
                // Move focus to first actionable item
                const first = drawer.querySelector('a,button,input,select,textarea');
                if(first) first.focus();
            }
            if(backdrop){ backdrop.classList.remove('hidden'); }
            if(profileMenu){ profileMenu.classList.add('hidden'); }
        }
        function closeDrawer(){
            if(drawer){
                drawer.classList.remove('open');
                drawer.setAttribute('aria-hidden','true');
                setTimeout(()=>drawer.classList.add('hidden'),200);
            }
            if(backdrop){ backdrop.classList.add('hidden'); }
            // Return focus to profile button
            if(pbtn){ pbtn.focus(); }
        }

        if(pbtn){ pbtn.onclick = (e)=>{ e.stopPropagation(); openDrawer(); }; }
        if(backdrop){ backdrop.onclick = ()=> closeDrawer(); }
        if(drawerClose){ drawerClose.onclick = ()=> closeDrawer(); }
        document.addEventListener('keydown', (e)=>{ if(e.key === 'Escape') closeDrawer(); });

        // Keep dropdown for large screens if needed
        if(pbtn && profileMenu){
            // Optional: show small dropdown on right-click
            pbtn.oncontextmenu = (e)=>{ e.preventDefault(); profileMenu.classList.toggle('hidden'); };
            document.addEventListener('click', (e)=>{
                if(!pbtn.contains(e.target) && !profileMenu.contains(e.target)){
                    profileMenu.classList.add('hidden');
                }
            });
        }

        // Drawer option handlers
        const drawerOptions = {
            'd-menu-profile': () => toast('Profile settings coming soon'),
            'menu-feedback': () => openFb(),
            'd-menu-feedback': () => openFb(),
            'd-menu-history': () => {
                toast('Loading past readings...');
                const tab = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target === 'analysis-section');
                if(tab) tab.click();
            },
            'd-menu-settings': () => toast('Settings panel coming soon'),
            'd-menu-help': () => {
                toast('Opening help center...');
                const tab = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target === 'features-section');
                if(tab) tab.click();
            },
            'd-menu-refer': () => toast('Refer a friend: code FEMP2025'),
            'd-menu-support': () => toast('Support: support@femplus.health'),
            'd-menu-contact': () => toast('Contact: support@femplus.health, +91 98765 43210'),
            'd-menu-about': () => {
                const tab = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target === 'home-section');
                if(tab) tab.click();
            },
            // Open Profile page and load data
            'menu-profile': () => {
                const tab = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target === 'profile-section');
                if(tab) tab.click();
                loadProfile();
            },
            'd-menu-profile': () => {
                const tab = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target === 'profile-section');
                if(tab) tab.click();
                loadProfile();
            },
            'd-logout-btn': () => {
                localStorage.removeItem('AUTH_TOKEN');
                localStorage.removeItem('AUTH_EMAIL');
                document.getElementById('profile')?.classList.add('hidden');
                showWelcomeSection();
                toast('Logged out');
                toggleAuthTabs(true);
            },
            'd-delete-account-btn': () => {
                if(confirm('Are you sure you want to delete your account permanently? This action cannot be undone.')){
                    toast('Account deletion coming soon. Contact support to proceed.');
                }
            }
        };
        Object.entries(drawerOptions).forEach(([id, handler]) => {
            const el = document.getElementById(id);
            if(el){ el.onclick = (e)=>{ e.preventDefault(); closeDrawer(); handler(); }; }
        });

        // Minimal AI assistant
        const fab = document.getElementById('ai-fab');
        const chat = document.getElementById('ai-chat');
        const aiClose = document.getElementById('ai-close');
        const aiSend = document.getElementById('ai-send');
        const aiText = document.getElementById('ai-text');
        const aiMsgs = document.getElementById('ai-messages');

        function addMsg(from, text){
            if(!aiMsgs) return;
            const div = document.createElement('div');
            div.textContent = `${from}: ${text}`;
            aiMsgs.appendChild(div);
            aiMsgs.scrollTop = aiMsgs.scrollHeight;
        }
        function openChat(){ if(chat){ chat.classList.remove('hidden'); chat.setAttribute('aria-hidden','false'); } }
        function closeChat(){ if(chat){ chat.classList.add('hidden'); chat.setAttribute('aria-hidden','true'); } }
        if(fab){ fab.onclick = ()=> openChat(); }
        if(aiClose){ aiClose.onclick = ()=> closeChat(); }
        if(aiSend){ aiSend.onclick = ()=> {
            const q = (aiText?.value || '').trim();
            if(!q) return;
            addMsg('You', q);
            if(aiText) aiText.value='';
            const to = (sel)=> Array.from(document.querySelectorAll('.tab')).find(t=>t.dataset.target===sel)?.click();
            if(/add reading|reading/i.test(q)) { addMsg('AI','Opening Add Reading...'); to('reading-section'); }
            else if(/feature|what can you do/i.test(q)) { addMsg('AI','Opening Features...'); to('features-section'); }
            else if(/shop|buy/i.test(q)) { addMsg('AI','Opening Shop...'); to('shop-section'); }
            else if(/lab|test/i.test(q)) { addMsg('AI','Opening Lab Tests...'); to('labs-section'); }
            else if(/login|sign in/i.test(q)) { addMsg('AI','Opening Login...'); to('login-section'); }
            else if(/sign up|register/i.test(q)) { addMsg('AI','Opening Sign Up...'); to('signup-section'); }
            else { addMsg('AI','I can help you navigate. Try: "open features"'); }
        }; }

        // Feedback modal
        const fbBackdrop = document.getElementById('fb-backdrop');
        const fbOpen = document.getElementById('open-feedback');
        const fbCancel = document.getElementById('fb-cancel');
        const fbSubmit = document.getElementById('fb-submit');
        const fbStars = document.getElementById('fb-stars');
        const fbList = document.getElementById('fb-list');
        let fbRating = 0;
        function openFb(){ if(fbBackdrop){ fbBackdrop.classList.remove('hidden'); fbBackdrop.setAttribute('aria-hidden','false'); } }
        function closeFb(){ if(fbBackdrop){ fbBackdrop.classList.add('hidden'); fbBackdrop.setAttribute('aria-hidden','true'); } }
        if(fbOpen){ fbOpen.onclick = ()=> openFb(); }
        if(fbCancel){ fbCancel.onclick = ()=> closeFb(); }
        if(fbStars){
            fbStars.querySelectorAll('button').forEach(btn=>{
                btn.onclick = ()=>{
                    fbRating = Number(btn.dataset.star);
                    fbStars.querySelectorAll('button').forEach(b=> b.classList.toggle('active', Number(b.dataset.star) <= fbRating));
                };
            });
        }
        if(fbSubmit){
            fbSubmit.onclick = async ()=>{
                if(!fbRating){ toast('Please select a rating', 'err'); return; }
                const comment = document.getElementById('fb-comment')?.value || '';
                try{
                    const res = await fetch(api('/feedback/'),{
                        method:'POST',
                        headers: { 'Content-Type':'application/json' },
                        body: JSON.stringify({ rating: fbRating, comment, context_type: 'home', user_email: localStorage.getItem('AUTH_EMAIL') || null })
                    });
                    await safeJson(res);
                    toast('Thanks for your feedback!');
                    closeFb();
                    loadFeedbackList();
                }catch(err){
                    toast(String(err.message||err),'err');
                }
            };
        }

        // Feedback list within modal (account only)
        async function loadFeedbackList(){
            if(!fbList) return;
            try{
                const res = await fetch(api('/feedback/public?limit=20'));
                const items = await safeJson(res);
                fbList.innerHTML = '';
                items.forEach((f)=>{
                    const card = document.createElement('div');
                    card.className = 'feedback-card';
                    const stars = '★'.repeat(f.rating) + '☆'.repeat(5 - f.rating);
                    card.innerHTML = `<div class=\"stars\">${stars}</div><div>${(f.comment||'').slice(0,240)}</div><small>${f.user_email||'Anonymous'}</small>`;
                    fbList.appendChild(card);
                });
            }catch(err){ /* ignore */ }
        }
        // Preload recent feedback for the modal
        loadFeedbackList();
    };
    if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else ready();
})();

function bearer(){
    const t = localStorage.getItem('AUTH_TOKEN');
    return t ? `Bearer ${t}` : '';
}

function numOrNull(v){
    if(v === undefined || v === null) return null;
    const s = String(v).trim();
    if(!s) return null;
    const n = Number(s);
    return Number.isFinite(n) ? n : null;
}

function emptyToUndefined(v){
    const s = String(v||'').trim();
    return s ? s : undefined;
}

async function safeJson(res){
    let data = null;
    try{ data = await res.json(); }
    catch(_){ data = { detail: 'No JSON response' }; }
    if(!res.ok){
        const msg = (data && (data.detail || data.message)) || `HTTP ${res.status}`;
        throw new Error(msg);
    }
    return data;
}

function showLoggedInUI(email){
    const prof = document.getElementById('profile');
    if(prof){ prof.classList.remove('hidden'); }
    const logout = document.getElementById('logout-btn');
    if(logout){
        logout.onclick = () => {
            localStorage.removeItem('AUTH_TOKEN');
            localStorage.removeItem('AUTH_EMAIL');
            document.getElementById('profile')?.classList.add('hidden');
            document.getElementById('profile-menu')?.classList.add('hidden');
            showWelcomeSection();
            toast('Logged out');
            toggleAuthTabs(true);
        };
    }
}

// Fetch and render profile
async function loadProfile(){
    try{
        const headers = {};
        const b = bearer();
        if(!b){ toast('Please login to view profile','err'); return; }
        headers['Authorization'] = b;
        const res = await fetch(api('/auth/me'),{ headers });
        const data = await safeJson(res);
        const el = document.getElementById('profile-content');
        if(el){
            el.innerHTML = `
                <div><strong>User ID</strong><div>${data.id}</div></div>
                <div><strong>Email</strong><div>${data.email}</div></div>
                <div><strong>Phone</strong><div>${data.phone || '-'}</div></div>
                <div><strong>Age</strong><div>${data.age ?? '-'}</div></div>
                <div><strong>Height (cm)</strong><div>${data.height_cm ?? '-'}</div></div>
                <div><strong>Blood Group</strong><div>${data.blood_group || '-'}</div></div>
            `;
        }
    }catch(e){ toast(String(e),'err'); }
}

function toggleAuthTabs(show){
    const signupTab = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target==='signup-section');
    const loginTab = Array.from(document.querySelectorAll('.tab')).find(t => t.dataset.target==='login-section');
    if(signupTab){ signupTab.style.display = show ? '' : 'none'; }
    if(loginTab){ loginTab.style.display = show ? '' : 'none'; }
}

function setTabsForAuth(isAuthed){
    const tabs = document.querySelectorAll('.tabbar .tab');
    tabs.forEach(tab => {
        const target = tab.getAttribute('data-target');
        const isPublic = target==='home-section' || target==='signup-section' || target==='login-section';
        if(isAuthed){
            // After login, show everything
            tab.style.display = '';
        } else {
            // Before login, only show Home/SignUp/Login
            tab.style.display = isPublic ? '' : 'none';
        }
    });
    // CTA consult button visibility
    const cta = document.getElementById('cta-consult');
    if(cta){ cta.style.display = isAuthed ? '' : 'none'; }
}

function showWelcomeSection(){
    const welcomeSection = document.getElementById('welcome-section');
    const dashboardSection = document.getElementById('dashboard-section');
    if(welcomeSection) welcomeSection.classList.remove('hidden');
    if(dashboardSection) dashboardSection.classList.add('hidden');
}

function showDashboardSection(){
    const welcomeSection = document.getElementById('welcome-section');
    const dashboardSection = document.getElementById('dashboard-section');
    if(welcomeSection) welcomeSection.classList.add('hidden');
    if(dashboardSection) dashboardSection.classList.remove('hidden');
}

function prefillAnalysisEmail(){
    const savedEmail = localStorage.getItem('AUTH_EMAIL');
    if(savedEmail) {
        const analysisEmail = document.getElementById('analysis-email');
        if(analysisEmail) analysisEmail.value = savedEmail;
    }
}

// Google Calendar Integration
function initGoogleCalendar() {
    // This is a placeholder for Google Calendar API integration
    // In a real implementation, you would:
    // 1. Set up OAuth 2.0 authentication
    // 2. Request calendar permissions
    // 3. Fetch menstrual cycle events
    // 4. Calculate cycle days automatically
    
    console.log('Google Calendar integration placeholder');
    
    // Example of how it would work:
    /*
    gapi.load('client', () => {
        gapi.client.init({
            apiKey: 'YOUR_API_KEY',
            clientId: 'YOUR_CLIENT_ID',
            discoveryDocs: ['https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest'],
            scope: 'https://www.googleapis.com/auth/calendar.readonly'
        }).then(() => {
            return gapi.client.calendar.events.list({
                calendarId: 'primary',
                timeMin: new Date().toISOString(),
                maxResults: 10,
                singleEvents: true,
                orderBy: 'startTime'
            });
        }).then(response => {
            const events = response.result.items;
            // Process menstrual cycle events
            updateCycleDay(events);
        });
    });
    */
}

function updateCycleDay(events) {
    // Placeholder function to calculate cycle day from calendar events
    // This would analyze menstrual cycle events and calculate current cycle day
    console.log('Updating cycle day from calendar events:', events);
}

// Features data and rendering
const FEATURES = [
    { key:'flow', title: 'Blood Flow Tracking', desc: 'Detect heavy or irregular bleeding', tier: 'free' },
    { key:'biomarkers', title: 'Biomarker Detection', desc: 'Hormones, proteins, RNA/DNA', tier: 'premium' },
    { key:'pain', title: 'Pain Monitoring', desc: 'Track cramps & inflammation', tier: 'free' },
    { key:'pid', title: 'PID Screening', desc: 'Pelvic inflammatory disease risk signals', tier: 'premium', diseaseType: 'PID' },
    { key:'pcos', title: 'PCOS/PCOD Insights', desc: 'Hormonal pattern analysis and trends', tier: 'premium', diseaseType: 'PCOS' },
    { key:'ovarian', title: 'Ovarian Cancer Signals', desc: 'Early risk indicators (research)', tier: 'premium', diseaseType: 'Cancer' },
    { key:'endo', title: 'Endometriosis Markers', desc: 'Pattern detection and flare tracking', tier: 'premium', diseaseType: 'Endometriosis' },
    { key:'anemia', title: 'Anemia Check', desc: 'Hemoglobin trends and alerts', tier: 'free' },
    { key:'consult', title: 'Doctor Consultation', desc: 'Teleconsults with gynecologists', tier: 'premium' },
];

// Disease-specific parameters configuration
const DISEASE_PARAMETERS = {
    'PCOS': {
        title: 'PCOS/PCOD Diagnosis',
        description: 'Comprehensive screening for Polycystic Ovary Syndrome',
        parameters: {
            manual: [
                { name: 'lh_level', label: 'LH Level (mIU/mL)', type: 'number', normal: '2-15', critical: '>15' },
                { name: 'fsh_level', label: 'FSH Level (mIU/mL)', type: 'number', normal: '3-10', critical: '<8' },
                { name: 'amh_level', label: 'AMH Level (ng/mL)', type: 'number', normal: '1-4', critical: '>4' },
                { name: 'androgens', label: 'Testosterone (ng/dL)', type: 'number', normal: '20-80', critical: '>80' },
                { name: 'blood_glucose', label: 'Blood Glucose (mg/dL)', type: 'number', normal: '70-100', critical: '>100' },
                { name: 'weight_gain', label: 'Weight Gain (kg)', type: 'number', normal: '0-2', critical: '>5' },
                { name: 'acne_severity', label: 'Acne Severity (0-5)', type: 'range', min: 0, max: 5, normal: '0-1', critical: '>3' },
                { name: 'insulin_resistance', label: 'HOMA-IR Score', type: 'number', normal: '<2.5', critical: '>2.5' }
            ],
            symptoms: [
                { name: 'irregular_cycle', label: 'Irregular menstrual cycle', type: 'checkbox' },
                { name: 'weight_gain', label: 'Unexplained weight gain', type: 'checkbox' },
                { name: 'acne', label: 'Severe acne', type: 'checkbox' },
                { name: 'hirsutism', label: 'Excessive hair growth', type: 'checkbox' },
                { name: 'hair_loss', label: 'Hair loss/thinning', type: 'checkbox' }
            ]
        }
    },
    'PID': {
        title: 'PID (Pelvic Inflammatory Disease) Screening',
        description: 'Detection of pelvic inflammatory disease and related infections',
        parameters: {
            manual: [
                { name: 'crp', label: 'CRP Level (mg/L)', type: 'number', normal: '<3', critical: '>10' },
                { name: 'wbc_count', label: 'WBC Count (/µL)', type: 'number', normal: '4000-11000', critical: '>11000' },
                { name: 'fever', label: 'Body Temperature (°C)', type: 'number', normal: '36.1-37.2', critical: '>37.5' },
                { name: 'vaginal_ph', label: 'Vaginal pH', type: 'number', normal: '4.0-4.5', critical: '<4.0 or >4.5' },
                { name: 'esr', label: 'ESR (mm/hr)', type: 'number', normal: '<20', critical: '>20' },
                { name: 'tenderness', label: 'Pelvic Tenderness (0-3)', type: 'range', min: 0, max: 3, normal: '0', critical: '>1' }
            ],
            symptoms: [
                { name: 'fever', label: 'Fever', type: 'checkbox' },
                { name: 'vaginal_discharge', label: 'Abnormal vaginal discharge', type: 'checkbox' },
                { name: 'discharge_odor', label: 'Foul-smelling discharge', type: 'checkbox' },
                { name: 'pelvic_pain', label: 'Lower abdominal pain', type: 'checkbox' },
                { name: 'painful_urination', label: 'Painful urination', type: 'checkbox' }
            ]
        }
    },
    'Endometriosis': {
        title: 'Endometriosis Risk Assessment',
        description: 'Comprehensive evaluation for endometriosis markers and symptoms',
        parameters: {
            manual: [
                { name: 'estrogen', label: 'Estrogen Level (pg/mL)', type: 'number', normal: '50-350', critical: '>350' },
                { name: 'ca125', label: 'CA-125 Level (U/mL)', type: 'number', normal: '<35', critical: '>35' },
                { name: 'pain_score', label: 'Pain Score (0-10)', type: 'range', min: 0, max: 10, normal: '0-3', critical: '>7' },
                { name: 'progesterone', label: 'Progesterone (ng/mL)', type: 'number', normal: '<1 (follicular), >5 (luteal)', critical: 'Abnormal pattern' }
            ],
            symptoms: [
                { name: 'severe_pain', label: 'Severe menstrual cramps', type: 'checkbox' },
                { name: 'pain_during_intercourse', label: 'Pain during intercourse', type: 'checkbox' },
                { name: 'heavy_bleeding', label: 'Heavy menstrual bleeding', type: 'checkbox' },
                { name: 'infertility', label: 'Difficulty conceiving', type: 'checkbox' },
                { name: 'bowel_symptoms', label: 'Painful bowel movements', type: 'checkbox' }
            ]
        }
    },
    'Cancer': {
        title: 'Ovarian Cancer Risk Assessment',
        description: 'Early detection markers for ovarian cancer (research-based)',
        parameters: {
            manual: [
                { name: 'ca125', label: 'CA-125 Level (U/mL)', type: 'number', normal: '<35', critical: '>35' },
                { name: 'estrogen', label: 'Estrogen Level (pg/mL)', type: 'number', normal: '50-350', critical: 'Abnormal levels' },
                { name: 'weight_loss', label: 'Unexplained Weight Loss (kg)', type: 'number', normal: '0-2', critical: '>5' },
                { name: 'age_factor', label: 'Age Factor', type: 'select', options: ['<40', '40-50', '50-60', '>60'], critical: '>50' }
            ],
            symptoms: [
                { name: 'bloating', label: 'Persistent bloating', type: 'checkbox' },
                { name: 'appetite_loss', label: 'Loss of appetite', type: 'checkbox' },
                { name: 'weight_loss', label: 'Unexplained weight loss', type: 'checkbox' },
                { name: 'pelvic_pain', label: 'Persistent pelvic pain', type: 'checkbox' },
                { name: 'urinary_symptoms', label: 'Frequent urination', type: 'checkbox' }
            ]
        }
    }
};

function isPremium(){
    return localStorage.getItem('PREMIUM') === '1';
}

function renderFeatures(){
    const makeCard = (f) => {
        const premium = f.tier === 'premium';
        const badge = premium ? '<span class="pill pill-premium badge">Premium</span>' : '<span class="pill badge">Free</span>';
        const lockedClass = premium && !isPremium() ? ' locked' : '';
        return `<div class="feature${lockedClass}" data-key="${f.key}" data-tier="${f.tier}"><h4>${f.title} ${badge}</h4><p>${f.desc}</p></div>`;
    };
    const home = document.getElementById('features-home');
    const gridFree = document.getElementById('features-grid-free');
    const gridPremium = document.getElementById('features-grid-premium');
    if(home){ home.innerHTML = FEATURES.slice(0,3).map(makeCard).join(''); }
    if(gridFree){ gridFree.innerHTML = FEATURES.filter(f=>f.tier==='free').map(makeCard).join(''); }
    if(gridPremium){ gridPremium.innerHTML = FEATURES.filter(f=>f.tier==='premium').map(makeCard).join(''); }

    // Click gating
    document.querySelectorAll('.feature').forEach(card => {
        card.addEventListener('click', () => {
            const tier = card.getAttribute('data-tier');
            const featureKey = card.getAttribute('data-key');
            
            if(tier === 'premium' && !isPremium()){
                openPremiumModal();
                return;
            }
            
            // Check if this is a disease-specific feature
            const feature = FEATURES.find(f => f.key === featureKey);
            if(feature && feature.diseaseType) {
                openDiseaseSpecificModal(feature.diseaseType);
            } else {
                toast(`${featureKey} opening...`);
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', renderFeatures);

// Disease-specific modal functions
function openDiseaseSpecificModal(diseaseType) {
    const config = DISEASE_PARAMETERS[diseaseType];
    if (!config) return;
    
    // Create modal HTML
    const modalHTML = `
        <div id="disease-modal-backdrop" class="modal-backdrop" aria-hidden="false">
            <div class="modal disease-modal" role="dialog" aria-modal="true">
                <div class="modal-header">
                    <h3>${config.title}</h3>
                    <button id="close-disease-modal" class="mini">×</button>
                </div>
                <div class="modal-content">
                    <p class="disease-description">${config.description}</p>
                    
                    <!-- Input Method Tabs -->
                    <div class="input-method-tabs">
                        <button class="method-tab active" data-method="manual">📝 Manual Entry</button>
                        <button class="method-tab" data-method="device">📱 Device Data</button>
                        <button class="method-tab" data-method="image">📷 Image Analysis</button>
                    </div>
                    
                    <!-- Manual Input Section -->
                    <div id="manual-input" class="input-section active">
                        <h4>Biomarker Parameters</h4>
                        <div class="parameter-grid">
                            ${config.parameters.manual.map(param => createParameterInput(param)).join('')}
                        </div>
                        
                        <h4>Symptoms Checklist</h4>
                        <div class="symptoms-checklist">
                            ${config.parameters.symptoms.map(symptom => createSymptomCheckbox(symptom)).join('')}
                        </div>
                    </div>
                    
                    <!-- Device Data Section -->
                    <div id="device-input" class="input-section">
                        <div class="device-connection">
                            <h4>Connect Device</h4>
                            <p>Pair your FemPlus device to automatically collect biomarker data.</p>
                            <button id="connect-device-btn" class="primary">Connect Device</button>
                            <div id="device-status" class="device-status">Not Connected</div>
                        </div>
                        <div id="device-data-display" class="device-data hidden">
                            <h4>Device Readings</h4>
                            <div class="device-readings"></div>
                        </div>
                    </div>
                    
                    <!-- Image Analysis Section -->
                    <div id="image-input" class="input-section">
                        <h4>Image Analysis</h4>
                        <p>Upload an image of your menstrual blood sample for AI analysis.</p>
                        <input type="file" id="disease-image-input" accept="image/*" />
                        <div id="image-preview" class="image-preview hidden">
                            <img id="preview-img" src="" alt="Sample preview" />
                            <button id="analyze-image-btn" class="primary">Analyze Image</button>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="modal-actions">
                        <button id="analyze-disease-btn" class="primary">Analyze ${diseaseType} Risk</button>
                        <button id="save-disease-data-btn" class="secondary">Save Data</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Setup event listeners
    setupDiseaseModalListeners(diseaseType);
}

function createParameterInput(param) {
    const { name, label, type, normal, critical, min, max, options } = param;
    
    let inputHTML = '';
    switch(type) {
        case 'number':
            inputHTML = `<input type="number" id="${name}" name="${name}" step="0.1" placeholder="${normal}" />`;
            break;
        case 'range':
            inputHTML = `<input type="range" id="${name}" name="${name}" min="${min}" max="${max}" value="0" />
                        <span class="range-value" id="${name}-value">0</span>`;
            break;
        case 'select':
            const optionHTML = options.map(opt => `<option value="${opt}">${opt}</option>`).join('');
            inputHTML = `<select id="${name}" name="${name}"><option value="">Select...</option>${optionHTML}</select>`;
            break;
        default:
            inputHTML = `<input type="text" id="${name}" name="${name}" placeholder="${normal}" />`;
    }
    
    return `
        <div class="parameter-item">
            <label for="${name}">${label}</label>
            ${inputHTML}
            <div class="parameter-info">
                <small class="normal-range">Normal: ${normal}</small>
                <small class="critical-range">Critical: ${critical}</small>
            </div>
        </div>
    `;
}

function createSymptomCheckbox(symptom) {
    return `
        <div class="symptom-item">
            <label>
                <input type="checkbox" name="${symptom.name}" />
                ${symptom.label}
            </label>
        </div>
    `;
}

function setupDiseaseModalListeners(diseaseType) {
    const modal = document.getElementById('disease-modal-backdrop');
    const closeBtn = document.getElementById('close-disease-modal');
    const methodTabs = document.querySelectorAll('.method-tab');
    const analyzeBtn = document.getElementById('analyze-disease-btn');
    
    // Close modal
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });
    
    // Method tab switching
    methodTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const method = tab.dataset.method;
            
            // Update tab states
            methodTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Show/hide sections
            document.querySelectorAll('.input-section').forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(`${method}-input`).classList.add('active');
        });
    });
    
    // Range value updates
    document.querySelectorAll('input[type="range"]').forEach(range => {
        range.addEventListener('input', () => {
            const valueSpan = document.getElementById(`${range.id}-value`);
            if (valueSpan) {
                valueSpan.textContent = range.value;
            }
        });
    });
    
    // Image upload handling
    const imageInput = document.getElementById('disease-image-input');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewImg.src = e.target.result;
                imagePreview.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Analyze button
    analyzeBtn.addEventListener('click', () => {
        analyzeDiseaseRisk(diseaseType);
    });
}

function analyzeDiseaseRisk(diseaseType) {
    const formData = collectDiseaseFormData(diseaseType);
    
    // Show loading state
    const analyzeBtn = document.getElementById('analyze-disease-btn');
    const originalText = analyzeBtn.textContent;
    analyzeBtn.textContent = 'Analyzing...';
    analyzeBtn.disabled = true;
    
    // Send data for analysis (simulate API call)
    setTimeout(() => {
        // Reset button
        analyzeBtn.textContent = originalText;
        analyzeBtn.disabled = false;
        
        // Show results (mock for now)
        showDiseaseAnalysisResults(diseaseType, formData);
    }, 2000);
}

function collectDiseaseFormData(diseaseType) {
    const config = DISEASE_PARAMETERS[diseaseType];
    const data = {
        diseaseType: diseaseType,
        parameters: {},
        symptoms: {}
    };
    
    // Collect manual parameters
    config.parameters.manual.forEach(param => {
        const element = document.getElementById(param.name);
        if (element) {
            data.parameters[param.name] = element.type === 'checkbox' ? element.checked : element.value;
        }
    });
    
    // Collect symptoms
    config.parameters.symptoms.forEach(symptom => {
        const element = document.querySelector(`input[name="${symptom.name}"]`);
        if (element) {
            data.symptoms[symptom.name] = element.checked;
        }
    });
    
    return data;
}

function showDiseaseAnalysisResults(diseaseType, formData) {
    // Create results modal
    const resultsHTML = `
        <div id="disease-results-backdrop" class="modal-backdrop" aria-hidden="false">
            <div class="modal disease-results" role="dialog" aria-modal="true">
                <div class="modal-header">
                    <h3>${diseaseType} Analysis Results</h3>
                    <button id="close-results-modal" class="mini">×</button>
                </div>
                <div class="modal-content">
                    <div class="risk-assessment">
                        <div class="risk-level high">
                            <h4>Risk Level: HIGH</h4>
                            <p>Based on your parameters, there are significant indicators for ${diseaseType} risk.</p>
                        </div>
                    </div>
                    
                    <div class="parameter-analysis">
                        <h4>Parameter Analysis</h4>
                        <div class="analysis-grid">
                            ${Object.entries(formData.parameters).map(([key, value]) => 
                                `<div class="analysis-item">
                                    <span class="param-name">${key}</span>
                                    <span class="param-value">${value}</span>
                                    <span class="param-status ${getParameterStatus(key, value, diseaseType)}">${getParameterStatus(key, value, diseaseType).toUpperCase()}</span>
                                </div>`
                            ).join('')}
                        </div>
                    </div>
                    
                    <div class="recommendations">
                        <h4>Recommendations</h4>
                        <ul>
                            <li>Consult with a gynecologist immediately</li>
                            <li>Consider additional diagnostic tests</li>
                            <li>Monitor symptoms closely</li>
                            <li>Maintain regular follow-ups</li>
                        </ul>
                    </div>
                    
                    <div class="modal-actions">
                        <button id="book-consultation-btn" class="primary">Book Consultation</button>
                        <button id="save-results-btn" class="secondary">Save Results</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', resultsHTML);
    
    // Setup results modal listeners
    document.getElementById('close-results-modal').addEventListener('click', () => {
        document.getElementById('disease-results-backdrop').remove();
    });
    
    document.getElementById('book-consultation-btn').addEventListener('click', () => {
        toast('Redirecting to consultation booking...');
    });
}

function getParameterStatus(paramName, value, diseaseType) {
    // Mock status determination - in real implementation, this would use medical thresholds
    const config = DISEASE_PARAMETERS[diseaseType];
    const param = config.parameters.manual.find(p => p.name === paramName);
    
    if (!param || !value) return 'normal';
    
    // Simple threshold checking (mock implementation)
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return 'normal';
    
    // Example logic for some parameters
    if (paramName === 'crp' && numValue > 10) return 'critical';
    if (paramName === 'ca125' && numValue > 35) return 'critical';
    if (paramName === 'lh_level' && numValue > 15) return 'critical';
    
    return 'normal';
}

// Premium modal logic
function openPremiumModal(){
    const bd = document.getElementById('premium-backdrop');
    if(!bd) return;
    bd.classList.add('open');
    bd.setAttribute('aria-hidden','false');
}
function closePremiumModal(){
    const bd = document.getElementById('premium-backdrop');
    if(!bd) return;
    bd.classList.remove('open');
    bd.setAttribute('aria-hidden','true');
}
document.addEventListener('DOMContentLoaded', () => {
    const buy = document.getElementById('premium-buy');
    const close = document.getElementById('premium-close');
    const open = document.getElementById('d-menu-premium');
    if(open){ open.addEventListener('click', (e)=>{ e.preventDefault(); openPremiumModal(); }); }
    if(close){ close.addEventListener('click', closePremiumModal); }
    if(buy){ buy.addEventListener('click', ()=>{
        localStorage.setItem('PREMIUM','1');
        closePremiumModal();
        toast('You are now a Premium member!');
        renderFeatures();
    }); }
});

// Predict from Reading section
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('predict-from-reading');
    if(!btn) return;
    btn.addEventListener('click', async () => {
        const payload = {
            flow_ml: numOrNull(els('flow-ml').value) ?? 0,
            hb: numOrNull(els('hb').value) ?? 0,
            ph: numOrNull(els('ph').value) ?? 0,
            crp: numOrNull(els('crp').value) ?? 0,
            hba1c_ratio: numOrNull(els('hba1c').value) ?? 0,
            clots_score: numOrNull(els('clots').value) ?? 0,
            fsh_level: numOrNull(els('fsh').value) ?? 0,
            lh_level: numOrNull(els('lh').value) ?? 0,
            amh_level: numOrNull(els('amh').value) ?? 0,
            tsh_level: numOrNull(els('tsh').value) ?? 0,
            prolactin_level: numOrNull(els('prolactin').value) ?? 0,
            image_base64: getImageBase64(),
            label: undefined
        };
        try{
            const res = await fetch(api('/flow/predict'),{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
            const data = await safeJson(res);
            renderMlOutput('reading-predict-cards', data);
            toast('Prediction ready');
        }catch(e){ toast(String(e),'err'); }
    });
});

// Source tabs switching
document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.source-tab');
    const sections = {
        manual: document.getElementById('source-manual'),
        device: document.getElementById('source-device'),
        image: document.getElementById('source-image'),
        'gas-sensor': document.getElementById('source-gas-sensor')
    };
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            // Hide all sections
            Object.values(sections).forEach(section => {
                if(section) section.classList.add('hidden');
            });
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding section
            const target = tab.dataset.source;
            if(sections[target]) {
                sections[target].classList.remove('hidden');
            }
        });
    });
});

// Device Integration - Web Bluetooth
let connectedDevice = null;
let deviceService = null;
let deviceCharacteristic = null;

// Device pairing and connection
document.addEventListener('DOMContentLoaded', () => {
    const pairBtn = document.getElementById('pair-home-btn');
    const pairReadingBtn = document.getElementById('pair-reading-btn');
    const fetchBtn = document.getElementById('fetch-sensor-btn');
    
    if(pairBtn) pairBtn.addEventListener('click', pairDevice);
    if(pairReadingBtn) pairReadingBtn.addEventListener('click', pairDevice);
    if(fetchBtn) fetchBtn.addEventListener('click', fetchDeviceData);
});

async function pairDevice() {
    try {
        if (!navigator.bluetooth) {
            toast('Web Bluetooth not supported in this browser', 'err');
            return;
        }
        
        toast('Scanning for FemPlus devices...');
        
        // Request device with specific service UUID
        const device = await navigator.bluetooth.requestDevice({
            filters: [
                { namePrefix: 'FemPlus' },
                { namePrefix: 'FP-' }
            ],
            optionalServices: [
                '0000180a-0000-1000-8000-00805f9b34fb', // Device Information Service
                '0000180d-0000-1000-8000-00805f9b34fb', // Battery Service
                '12345678-1234-1234-1234-123456789abc'  // Custom FemPlus Service
            ]
        });
        
        toast('Connecting to device...');
        
        // Connect to GATT server
        const server = await device.gatt.connect();
        connectedDevice = device;
        
        // Get the custom service
        try {
            deviceService = await server.getPrimaryService('12345678-1234-1234-1234-123456789abc');
            deviceCharacteristic = await deviceService.getCharacteristic('12345678-1234-1234-1234-123456789abd');
        } catch (e) {
            // Fallback to Device Information Service for demo
            deviceService = await server.getPrimaryService('0000180a-0000-1000-8000-00805f9b34fb');
            deviceCharacteristic = await deviceService.getCharacteristic('00002a25-0000-1000-8000-00805f9b34fb');
        }
        
        toast('Device connected successfully!', 'ok');
        updateDeviceStatus('connected');
        
        // Listen for disconnection
        device.addEventListener('gattserverdisconnected', () => {
            connectedDevice = null;
            deviceService = null;
            deviceCharacteristic = null;
            updateDeviceStatus('disconnected');
            toast('Device disconnected', 'err');
        });
        
    } catch (error) {
        console.error('Device pairing failed:', error);
        if (error.name === 'NotFoundError') {
            toast('No FemPlus device found. Make sure device is on and in pairing mode.', 'err');
        } else if (error.name === 'SecurityError') {
            toast('Bluetooth access denied. Please allow Bluetooth permissions.', 'err');
        } else {
            toast(`Pairing failed: ${error.message}`, 'err');
        }
        updateDeviceStatus('error');
    }
}

async function fetchDeviceData() {
    if (!connectedDevice || !deviceCharacteristic) {
        toast('Please pair device first', 'err');
        return;
    }
    
    try {
        toast('Reading sensor data...');
        
        // Read current value
        const dataView = await deviceCharacteristic.readValue();
        const data = parseDeviceData(dataView);
        
        if (data) {
            autoFillForm(data);
            toast('Sensor data loaded successfully!', 'ok');
        } else {
            toast('Failed to parse device data', 'err');
        }
        
    } catch (error) {
        console.error('Data fetch failed:', error);
        toast(`Failed to read data: ${error.message}`, 'err');
    }
}

function parseDeviceData(dataView) {
    try {
        // Parse binary data from device
        // This is a mock parser - replace with actual device protocol
        const buffer = new Uint8Array(dataView.buffer);
        
        if (buffer.length < 44) { // Minimum expected data length
            return null;
        }
        
        // Mock data parsing (replace with actual device protocol)
        const data = {
            flow_ml: parseFloat32(buffer, 0),
            hb: parseFloat32(buffer, 4),
            ph: parseFloat32(buffer, 8),
            crp: parseFloat32(buffer, 12),
            hba1c_ratio: parseFloat32(buffer, 16),
            clots_score: parseFloat32(buffer, 20),
            fsh_level: parseFloat32(buffer, 24),
            lh_level: parseFloat32(buffer, 28),
            amh_level: parseFloat32(buffer, 32),
            tsh_level: parseFloat32(buffer, 36),
            prolactin_level: parseFloat32(buffer, 40)
        };
        
        return validateDeviceData(data);
        
    } catch (error) {
        console.error('Data parsing failed:', error);
        return null;
    }
}

function parseFloat32(buffer, offset) {
    const view = new DataView(buffer.buffer, buffer.byteOffset + offset, 4);
    return view.getFloat32(0, true); // little-endian
}

function validateDeviceData(data) {
    const ranges = {
        flow_ml: [0, 500],
        hb: [5, 20],
        ph: [3, 8],
        crp: [0, 100],
        hba1c_ratio: [3, 15],
        clots_score: [0, 5],
        fsh_level: [0, 50],
        lh_level: [0, 50],
        amh_level: [0, 20],
        tsh_level: [0, 10],
        prolactin_level: [0, 100],
        // New parameters
        esr: [0, 100],
        leukocyte_count: [1000, 20000],
        vaginal_ph: [3, 8],
        ca125: [0, 500],
        estrogen: [0, 1000],
        progesterone: [0, 50],
        androgens: [0, 200],
        blood_glucose: [50, 300],
        wbc_count: [1000, 20000],
        pain_score: [0, 10],
        weight_gain: [-20, 50],
        acne_severity: [0, 5],
        insulin_resistance: [0, 10],
        fever: [35, 42],
        tenderness: [0, 3],
        pain_during_intercourse: [0, 1],
        bloating: [0, 1],
        weight_loss: [0, 50],
        appetite_loss: [0, 1]
    };
    
    const validated = {};
    let hasValidData = false;
    
    for (const [key, value] of Object.entries(data)) {
        if (value !== null && !isNaN(value) && isFinite(value)) {
            const [min, max] = ranges[key] || [0, 1000];
            if (value >= min && value <= max) {
                validated[key] = value;
                hasValidData = true;
            } else {
                console.warn(`Value out of range for ${key}: ${value}`);
            }
        }
    }
    
    return hasValidData ? validated : null;
}

function autoFillForm(data) {
    const fieldMap = {
        flow_ml: 'flow-ml',
        hb: 'hb',
        ph: 'ph',
        crp: 'crp',
        hba1c_ratio: 'hba1c',
        clots_score: 'clots',
        fsh_level: 'fsh',
        lh_level: 'lh',
        amh_level: 'amh',
        tsh_level: 'tsh',
        prolactin_level: 'prolactin',
        // New parameters
        esr: 'esr',
        leukocyte_count: 'leukocyte_count',
        vaginal_ph: 'vaginal_ph',
        ca125: 'ca125',
        estrogen: 'estrogen',
        progesterone: 'progesterone',
        androgens: 'androgens',
        blood_glucose: 'blood_glucose',
        wbc_count: 'wbc_count',
        pain_score: 'pain_score',
        weight_gain: 'weight_gain',
        acne_severity: 'acne_severity',
        insulin_resistance: 'insulin_resistance',
        fever: 'fever',
        tenderness: 'tenderness',
        pain_during_intercourse: 'pain_during_intercourse',
        bloating: 'bloating',
        weight_loss: 'weight_loss',
        appetite_loss: 'appetite_loss'
    };
    
    let filledCount = 0;
    
    for (const [dataKey, fieldId] of Object.entries(fieldMap)) {
        if (data[dataKey] !== undefined) {
            const field = els(fieldId);
            if (field) {
                field.value = data[dataKey].toFixed(2);
                field.style.backgroundColor = '#f0fff0'; // Light green to indicate auto-filled
                filledCount++;
            }
        }
    }
    
    if (filledCount > 0) {
        toast(`Auto-filled ${filledCount} readings from device`);
        // Enable Get Output button
        const outputBtn = document.getElementById('predict-from-reading');
        if (outputBtn) {
            outputBtn.disabled = false;
            outputBtn.style.opacity = '1';
        }
    } else {
        toast('No valid readings found in device data', 'err');
    }
}

function updateDeviceStatus(status) {
    const statusElements = document.querySelectorAll('.device-status');
    statusElements.forEach(el => {
        el.textContent = status === 'connected' ? 'Connected' : 
                        status === 'disconnected' ? 'Disconnected' : 
                        status === 'error' ? 'Error' : 'Not Connected';
        el.className = `device-status ${status}`;
    });
    
    // Update button states
    const pairBtns = document.querySelectorAll('#pair-home-btn, #pair-reading-btn');
    const fetchBtn = document.getElementById('fetch-sensor-btn');
    
    pairBtns.forEach(btn => {
        if (btn) btn.disabled = status === 'connected';
    });
    
    if (fetchBtn) {
        fetchBtn.disabled = status !== 'connected';
    }
}

// Health & Wellness functionality
document.addEventListener('DOMContentLoaded', () => {
    // Health tab switching
    const healthTabs = document.querySelectorAll('.health-tab');
    const healthContents = document.querySelectorAll('.health-content');
    
    healthTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            healthTabs.forEach(t => t.classList.remove('active'));
            healthContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding content
            const targetId = tab.getAttribute('data-health-target');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    // Diet tracking
    const addFoodBtn = document.getElementById('add-food-btn');
    if (addFoodBtn) {
        addFoodBtn.addEventListener('click', addFoodItem);
    }

    // Exercise tracking
    const logExerciseBtn = document.getElementById('log-exercise-btn');
    if (logExerciseBtn) {
        logExerciseBtn.addEventListener('click', logExercise);
    }

    // Load saved data
    loadHealthData();
});

// Diet tracking functions
let dailyFood = JSON.parse(localStorage.getItem('dailyFood') || '[]');
let dailyExercises = JSON.parse(localStorage.getItem('dailyExercises') || '[]');

function addFoodItem() {
    const foodItem = document.getElementById('food-item');
    const calories = document.getElementById('calories');
    
    if (!foodItem.value.trim()) {
        toast('Please enter a food item', 'err');
        return;
    }
    
    const food = {
        id: Date.now(),
        name: foodItem.value.trim(),
        calories: parseInt(calories.value) || 0,
        timestamp: new Date().toLocaleTimeString()
    };
    
    dailyFood.push(food);
    localStorage.setItem('dailyFood', JSON.stringify(dailyFood));
    
    updateNutritionSummary();
    updateFoodLog();
    
    // Clear inputs
    foodItem.value = '';
    calories.value = '';
    
    toast('Food item added successfully!', 'ok');
}

function updateNutritionSummary() {
    const totalCalories = dailyFood.reduce((sum, food) => sum + food.calories, 0);
    const totalIron = dailyFood.reduce((sum, food) => sum + getIronContent(food.name), 0);
    const totalProtein = dailyFood.reduce((sum, food) => sum + getProteinContent(food.name), 0);
    const totalFiber = dailyFood.reduce((sum, food) => sum + getFiberContent(food.name), 0);
    
    document.getElementById('total-calories').textContent = totalCalories;
    document.getElementById('total-iron').textContent = totalIron.toFixed(1) + 'mg';
    document.getElementById('total-protein').textContent = totalProtein.toFixed(1) + 'g';
    document.getElementById('total-fiber').textContent = totalFiber.toFixed(1) + 'g';
}

function updateFoodLog() {
    const foodItems = document.getElementById('food-items');
    if (!foodItems) return;
    
    if (dailyFood.length === 0) {
        foodItems.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 20px;">No food items logged today</p>';
        return;
    }
    
    const foodHtml = dailyFood.map(food => `
        <div class="food-item">
            <span>${food.name}</span>
            <span>${food.calories} cal • ${food.timestamp}</span>
        </div>
    `).join('');
    
    foodItems.innerHTML = foodHtml;
}

function getIronContent(foodName) {
    const ironMap = {
        'spinach': 2.7, 'lentils': 3.3, 'beef': 2.6, 'chicken': 1.0,
        'salmon': 0.8, 'eggs': 1.2, 'beans': 2.5, 'tofu': 3.4,
        'quinoa': 2.8, 'oats': 2.1, 'beetroot': 0.8, 'broccoli': 0.7
    };
    
    const lowerName = foodName.toLowerCase();
    for (const [key, value] of Object.entries(ironMap)) {
        if (lowerName.includes(key)) {
            return value;
        }
    }
    return 0.5; // Default iron content
}

function getProteinContent(foodName) {
    const proteinMap = {
        'chicken': 25, 'beef': 26, 'salmon': 25, 'eggs': 13,
        'tofu': 8, 'lentils': 9, 'beans': 8, 'quinoa': 4,
        'oats': 5, 'yogurt': 10, 'cheese': 7, 'nuts': 6
    };
    
    const lowerName = foodName.toLowerCase();
    for (const [key, value] of Object.entries(proteinMap)) {
        if (lowerName.includes(key)) {
            return value;
        }
    }
    return 3; // Default protein content
}

function getFiberContent(foodName) {
    const fiberMap = {
        'spinach': 2.2, 'broccoli': 2.6, 'carrots': 2.8, 'apples': 2.4,
        'bananas': 2.6, 'oats': 10, 'quinoa': 2.8, 'lentils': 7.9,
        'beans': 6.4, 'berries': 3.5, 'avocado': 6.7, 'sweet potato': 3.8
    };
    
    const lowerName = foodName.toLowerCase();
    for (const [key, value] of Object.entries(fiberMap)) {
        if (lowerName.includes(key)) {
            return value;
        }
    }
    return 1; // Default fiber content
}

// Exercise tracking functions
function logExercise() {
    const exerciseType = document.getElementById('exercise-type');
    const exerciseDuration = document.getElementById('exercise-duration');
    
    if (!exerciseDuration.value || exerciseDuration.value <= 0) {
        toast('Please enter a valid duration', 'err');
        return;
    }
    
    const exercise = {
        id: Date.now(),
        type: exerciseType.value,
        duration: parseInt(exerciseDuration.value),
        calories: calculateCaloriesBurned(exerciseType.value, parseInt(exerciseDuration.value)),
        timestamp: new Date().toLocaleTimeString()
    };
    
    dailyExercises.push(exercise);
    localStorage.setItem('dailyExercises', JSON.stringify(dailyExercises));
    
    updateExerciseSummary();
    updateExerciseLog();
    
    // Clear input
    exerciseDuration.value = '';
    
    toast('Exercise logged successfully!', 'ok');
}

function updateExerciseSummary() {
    const totalTime = dailyExercises.reduce((sum, exercise) => sum + exercise.duration, 0);
    const totalCalories = dailyExercises.reduce((sum, exercise) => sum + exercise.calories, 0);
    
    document.getElementById('total-exercise-time').textContent = totalTime + ' min';
    document.getElementById('calories-burned').textContent = totalCalories;
}

function updateExerciseLog() {
    const exerciseItems = document.getElementById('exercise-items');
    if (!exerciseItems) return;
    
    if (dailyExercises.length === 0) {
        exerciseItems.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 20px;">No exercises logged today</p>';
        return;
    }
    
    const exerciseHtml = dailyExercises.map(exercise => `
        <div class="exercise-item">
            <span>${exercise.type.charAt(0).toUpperCase() + exercise.type.slice(1)}</span>
            <span>${exercise.duration} min • ${exercise.calories} cal • ${exercise.timestamp}</span>
        </div>
    `).join('');
    
    exerciseItems.innerHTML = exerciseHtml;
}

function calculateCaloriesBurned(exerciseType, duration) {
    const caloriesPerMinute = {
        'walking': 4,
        'yoga': 3,
        'strength': 6,
        'cardio': 8,
        'stretching': 2,
        'dance': 5
    };
    
    return Math.round((caloriesPerMinute[exerciseType] || 4) * duration);
}

function loadHealthData() {
    // Load today's data
    const today = new Date().toDateString();
    const savedDate = localStorage.getItem('healthDataDate');
    
    if (savedDate !== today) {
        // New day - reset data
        dailyFood = [];
        dailyExercises = [];
        localStorage.setItem('dailyFood', JSON.stringify(dailyFood));
        localStorage.setItem('dailyExercises', JSON.stringify(dailyExercises));
        localStorage.setItem('healthDataDate', today);
    }
    
    updateNutritionSummary();
    updateFoodLog();
    updateExerciseSummary();
    updateExerciseLog();
}

function parseImageFile(file) {
    // We cannot synchronously read file; leave undefined; UI will send via predict form's textarea if provided manually.
    return undefined;
}

function filterFreePrediction(result){
    try{
        const r = JSON.parse(JSON.stringify(result));
        if(r.flags){
            // Hide premium disease flags
            delete r.flags.diabetes_flag; // treat as premium for demo
            // Keep anemia, ph_alert, inflammation, menorrhagia
        }
        if(r.premium_detail){ r.premium_detail = 'Upgrade to see detailed biomarkers and disease risks'; }
        return r;
    }catch(_){ return result; }
}

function levelToClass(level){
    if(!level) return 'low';
    const l = String(level).toLowerCase();
    if(l.includes('critical')) return 'critical';
    if(l.includes('high')) return 'high';
    if(l.includes('mod') || l.includes('med')) return 'moderate';
    if(l.includes('low')) return 'low';
    if(l.includes('no risk') || l.includes('good')) return 'no-risk';
    return 'low';
}

function renderRiskCards(targetId, flags, context){
    const target = document.getElementById(targetId);
    if(!target) return;

    const prediction = context.prediction || 'N/A';
    const risk_indicator = context.risk_indicator || 'N/A';
    const adviceList = context.advice || [];
    const probabilities = context.probabilities || {};
    const detectedConditions = context.detected_conditions || [];

    // Calculate risk counts for multiple indicators
    const highRiskCount = detectedConditions.filter(c => c.risk_level === 'High').length;
    const moderateRiskCount = detectedConditions.filter(c => c.risk_level === 'Moderate').length;
    const lowRiskCount = detectedConditions.filter(c => c.risk_level === 'Low').length;
    
    let outputHtml = `
        <div class="prediction-summary">
            <div class="risk-indicator-card ${levelToClass(risk_indicator)}">
                <strong>Overall Risk:</strong> <span>${risk_indicator}</span>
            </div>`;
    
    // Add multiple risk indicators if conditions are detected
    if (detectedConditions.length > 0) {
        const riskIndicators = [];
        if (highRiskCount > 0) riskIndicators.push(`🚨 HIGH RISK (${highRiskCount})`);
        if (moderateRiskCount > 0) riskIndicators.push(`⚠️ MODERATE RISK (${moderateRiskCount})`);
        if (lowRiskCount > 0) riskIndicators.push(`📊 LOW RISK (${lowRiskCount})`);
        
        outputHtml += `
            <div class="multiple-risk-indicators">
                <strong>Risk Breakdown:</strong> ${riskIndicators.join(' • ')}
            </div>`;
    } else {
        outputHtml += `
            <div class="no-risk-indicator">
                <strong>🎉 NO RISK DETECTED:</strong> <span>You are good to go!</span>
            </div>`;
    }
    
    outputHtml += `
            <div class="prediction-label">
                <strong>Primary Prediction:</strong> <span>${prediction}</span>
            </div>
        </div>
    `;

    // Display detected conditions
    if (detectedConditions.length > 0) {
        outputHtml += `<div class="detected-conditions">
            <h4>🔍 Detected Conditions (${detectedConditions.length})</h4>
            <div class="conditions-grid">`;
        
        detectedConditions.forEach(condition => {
            const riskClass = levelToClass(condition.risk_level);
            const confidence = Math.round(condition.confidence * 100);
            const matchedCount = condition.matched_count || 0;
            const totalCount = condition.total_count || 0;
            
            outputHtml += `
                <div class="condition-card ${riskClass}">
                    <div class="condition-header">
                        <strong>${condition.condition}</strong>
                        <span class="risk-badge ${riskClass}">${condition.risk_level}</span>
                    </div>
                    <div class="confidence">Confidence: ${confidence}% (${matchedCount}/${totalCount} biomarkers match)</div>
                    <div class="biomarkers">
                        ${Object.entries(condition.biomarkers).map(([key, value]) => 
                            `<span class="biomarker">${key}: ${value.toFixed(2)}</span>`
                        ).join(' • ')}
                    </div>
                </div>
            `;
        });
        
        outputHtml += `</div></div>`;
    }

    // Display individual risk flags (legacy support)
    const entries = Object.entries(flags || {});
    if(entries.length){
        const cards = entries.map(([k,v])=>{
            const cls = levelToClass(v);
            const title = k.replace(/_/g,' ');
            return `<div class="risk ${cls}"><strong>${title}</strong><div>Level: ${v}</div></div>`;
        }).join('');
        outputHtml += `<div class="risk-grid">${cards}</div>`;
    } else if (detectedConditions.length === 0) {
        outputHtml += `<p>No specific flags detected.</p>`;
    }

    // Display probabilities
    if (Object.keys(probabilities).length > 0) {
        const sortedProbs = Object.entries(probabilities).sort(([,a],[,b]) => b-a);
        const topProbs = sortedProbs.slice(0, 5).map(([label, prob]) => 
            `<li><span class="prob-label">${label}:</span> <span class="prob-value">${(prob * 100).toFixed(1)}%</span></li>`
        ).join('');
        outputHtml += `<div class="probabilities-box">
            <h4>📊 Prediction Probabilities</h4>
            <ul class="prob-list">${topProbs}</ul>
        </div>`;
    }

    // Display comprehensive advice
    if (adviceList.length > 0) {
        const adviceItems = adviceList.map(item => {
            if (item.startsWith('\n🔍') || item.startsWith('🔍')) {
                return `<li class="condition-advice">${item}</li>`;
            } else if (item.startsWith('•')) {
                return `<li class="advice-item">${item}</li>`;
            } else if (item.startsWith('\n📋') || item.startsWith('📋')) {
                return `<li class="section-header">${item}</li>`;
            } else {
                return `<li class="general-advice">${item}</li>`;
            }
        }).join('');
        
        outputHtml += `<div class="advice-box">
            <h4 class="advice-title">💡 Comprehensive Health Advice</h4>
            <ul class="advice-list">${adviceItems}</ul>
            <div class="action-buttons">
                <button class="mini primary" id="btn-consult-doc">Consult a Doctor</button>
                <button class="mini secondary" id="btn-home-remedy">Home Remedies</button>
                <button class="mini tertiary" id="btn-emergency">Emergency Care</button>
            </div>
        </div>`;
    } else {
        outputHtml += `<div class="advice-box">
            <h4 class="advice-title">💡 Health Advice</h4>
            <div>No specific advice available. Continue maintaining a healthy lifestyle.</div>
        </div>`;
    }

    target.innerHTML = outputHtml;
    
    // Add event listeners for action buttons
    const consultBtn = document.getElementById('btn-consult-doc');
    if(consultBtn){ 
        consultBtn.onclick = ()=> {
            const featuresTab = Array.from(document.querySelectorAll('.tab')).find(t=>t.dataset.target==='features-section');
            if(featuresTab) featuresTab.click();
            toast('Redirecting to doctor consultation...');
        };
    }
    
    const remedyBtn = document.getElementById('btn-home-remedy');
    if(remedyBtn){ 
        remedyBtn.onclick = ()=> {
            const remedies = [
                'Hydration: Drink 8-10 glasses of water daily',
                'Rest: Ensure 7-9 hours of quality sleep',
                'Warm compress: Apply to lower abdomen for pain relief',
                'Iron-rich diet: Include spinach, lentils, beetroot',
                'Gentle exercise: Walking, yoga, or light stretching',
                'Stress management: Meditation, deep breathing',
                'Avoid caffeine and alcohol during menstruation'
            ];
            toast(remedies.join(' | '), 'ok');
        };
    }
    
    const emergencyBtn = document.getElementById('btn-emergency');
    if(emergencyBtn){ 
        emergencyBtn.onclick = ()=> {
            toast('🚨 For emergencies, call your local emergency number or visit the nearest hospital immediately.', 'err');
        };
    }
}


function getImageBase64(){
    // Placeholder for image base64 conversion
    // In a real implementation, this would convert an uploaded image to base64
    return undefined;
}

function renderMlOutput(targetId, data){
    const target = document.getElementById(targetId);
    if(!target) return;
    const risk = String(data?.risk_indicator || 'Low');
    const cls = levelToClass(risk);
    const pred = data?.prediction || 'Unknown';
    const probs = data?.probabilities || {};
    const advice = Array.isArray(data?.advice) ? data.advice : [];
    const probList = Object.entries(probs).slice(0,3).map(([k,v])=>`<li>${k}: ${(v*100).toFixed(1)}%</li>`).join('');
    const adviceList = advice.map(a=>`<li>${a}</li>`).join('');
    target.innerHTML = `
        <div class="risk ${cls}"><strong>Overall risk</strong><div>${risk}</div></div>
        <div class="card" style="margin-top:8px">
            <div><strong>Prediction</strong>: ${pred}</div>
            ${probList ? `<ul style="margin-top:6px">${probList}</ul>` : ''}
        </div>
        <div class="advice-box" style="margin-top:8px">
            <h4 class="advice-title">Advice</h4>
            ${adviceList ? `<ul>${adviceList}</ul>` : '<div>No advice available.</div>'}
            <div style="margin-top:8px"><button class="mini" id="btn-consult-doc">Consult a Doctor</button> <button class="mini" id="btn-home-remedy">Home Remedies</button></div>
        </div>
    `;
    const cd = document.getElementById('btn-consult-doc');
    if(cd){ cd.onclick = ()=> Array.from(document.querySelectorAll('.tab')).find(t=>t.dataset.target==='features-section')?.click(); }
    const hr = document.getElementById('btn-home-remedy');
    if(hr){ hr.onclick = ()=> toast('Hydration, rest, warm compress, iron-rich diet (for anemia).'); }
}

// Gas Sensor Integration - ThingSpeak
let currentGasData = null;

document.addEventListener('DOMContentLoaded', () => {
    const fetchGasBtn = document.getElementById('fetch-gas-data-btn');
    const addGasReadingBtn = document.getElementById('add-gas-reading-btn');
    
    if(fetchGasBtn) fetchGasBtn.addEventListener('click', fetchGasSensorData);
    if(addGasReadingBtn) addGasReadingBtn.addEventListener('click', addGasSensorReading);
});

async function fetchGasSensorData() {
    try {
        toast('Fetching gas sensor data from ThingSpeak...');
        
        const response = await fetch('http://localhost:8000/data/gas-sensor/latest');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Handle null or empty response
        if (!data || data === null) {
            updateGasSensorStatus('error');
            toast('No data received from ThingSpeak API', 'err');
            return;
        }
        
        if (data.error) {
            // Handle configuration error
            updateGasSensorStatus('error');
            toast(data.message || data.error, 'err');
            displayGasSensorData(data); // Still display the error data
            return;
        }
        
        currentGasData = data;
        displayGasSensorData(data);
        updateGasSensorStatus('connected');
        document.getElementById('add-gas-reading-btn').disabled = false;
        toast('Gas sensor data loaded successfully!', 'ok');
    } catch (error) {
        console.error('Gas sensor fetch failed:', error);
        updateGasSensorStatus('error');
        toast(`Failed to fetch gas sensor data: ${error.message}`, 'err');
    }
}

function displayGasSensorData(data) {
    
    // Update AQI display
    const aqiValue = document.getElementById('aqi-value');
    const aqiCategory = document.getElementById('aqi-category');
    if (aqiValue) aqiValue.textContent = data.aqi !== undefined ? data.aqi : '--';
    if (aqiCategory) {
        aqiCategory.textContent = data.category || '--';
        aqiCategory.className = 'gas-category';
        if (data.category) {
            const category = data.category.toLowerCase();
            if (category.includes('good')) aqiCategory.classList.add('good');
            else if (category.includes('moderate')) aqiCategory.classList.add('moderate');
            else if (category.includes('unhealthy')) aqiCategory.classList.add('unhealthy');
        }
    }
    
    // Update individual sensor values
    const sensors = {
        'co2-value': data.co2_ppm,
        'co-value': data.co_ppm,
        'no2-value': data.no2_ppb,
        'o3-value': data.o3_ppb,
        'pm25-value': data.pm25_ugm3,
        'pm10-value': data.pm10_ugm3,
        'temp-value': data.temperature_c,
        'humidity-value': data.humidity_pct,
        // TCS230 Color sensor values
        'color-red-value': data.color_red,
        'color-green-value': data.color_green,
        'color-blue-value': data.color_blue,
        'color-clear-value': data.color_clear,
        'color-hue-value': data.color_hue,
        'color-saturation-value': data.color_saturation,
        'color-brightness-value': data.color_brightness,
        'color-category-value': data.color_category
    };
    
    Object.entries(sensors).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            if (value !== null && value !== undefined) {
                element.textContent = typeof value === 'number' ? value.toFixed(2) : value;
            } else {
                element.textContent = '--';
            }
        }
    });
    
    // Update timestamp and health concern
    const timestamp = document.getElementById('gas-sensor-timestamp');
    const healthConcern = document.getElementById('gas-sensor-health-concern');
    
    if (timestamp) {
        const date = new Date(data.timestamp || Date.now());
        timestamp.textContent = `Last updated: ${date.toLocaleString()}`;
    }
    
    if (healthConcern) {
        let healthText = data.health_concern || 'No data available';
        
        // Add color analysis if available
        if (data.color_analysis && data.color_analysis.health_indicators) {
            const colorIndicators = data.color_analysis.health_indicators.join(', ');
            healthText += ` | Color analysis: ${colorIndicators}`;
        }
        
        healthConcern.textContent = `Health concern: ${healthText}`;
    }
    
    // Show the display
    const display = document.getElementById('gas-sensor-display');
    if (display) {
        display.classList.remove('hidden');
    }
}

function updateGasSensorStatus(status) {
    const statusElement = document.getElementById('gas-sensor-status');
    if (statusElement) {
        statusElement.textContent = status === 'connected' ? 'Connected' : 
                                   status === 'error' ? 'Connection Error' : 'Not Connected';
        statusElement.className = 'device-status';
        if (status === 'connected') statusElement.classList.add('connected');
        else if (status === 'error') statusElement.classList.add('error');
    }
}

async function addGasSensorReading() {
    if (!currentGasData) {
        toast('Please fetch gas sensor data first', 'err');
        return;
    }
    
    const userEmail = document.getElementById('reading-email').value.trim();
    if (!userEmail) {
        toast('Please enter user email', 'err');
        return;
    }
    
    try {
        toast('Adding gas sensor reading...');
        
        const response = await fetch('http://localhost:8000/data/gas-sensor/add-reading', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_email: userEmail })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            toast('Gas sensor reading added successfully!', 'ok');
            // Reset the form
            document.getElementById('add-gas-reading-btn').disabled = true;
            currentGasData = null;
        } else {
            throw new Error(data.error || 'Failed to add gas sensor reading');
        }
    } catch (error) {
        console.error('Add gas reading failed:', error);
        toast(`Failed to add gas sensor reading: ${error.message}`, 'err');
    }
}


