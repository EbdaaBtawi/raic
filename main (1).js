// ── Session tracking for bounce rate ──────────────
function getCookie(n) {
    var v = document.cookie.match('(^|;)\\s*' + n + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
}
if (!getCookie('raic_sid')) {
    var sid = 'sid_' + Math.random().toString(36).slice(2) + Date.now();
    document.cookie = 'raic_sid=' + sid + ';path=/;max-age=1800';
}

// ── Time on page ───────────────────────────────────
var _pageStart = Date.now();
window.addEventListener('beforeunload', function () {
    var seconds = Math.round((Date.now() - _pageStart) / 1000);
    navigator.sendBeacon('/api/track_duration', JSON.stringify({
        page: window.location.pathname,
        seconds: seconds
    }));
});

// ── Form validation ────────────────────────────────
function validateJoinForm() {
    var name = document.getElementById("full_name").value.trim();
    var email = document.getElementById("email").value.trim();
    var studentId = document.getElementById("student_id").value.trim();
    var major = document.getElementById("major").value.trim();
    var interest = document.getElementById("interest").value;
    var error = document.getElementById("joinError");

    if (name === "" || email === "" || studentId === "" || major === "" || interest === "") {
        error.textContent = "All fields are required.";
        return false;
    }
    if (!email.includes("@") || !email.includes(".")) {
        error.textContent = "Please enter a valid email.";
        return false;
    }
    if (studentId.length < 5) {
        error.textContent = "Student ID must be at least 5 characters.";
        return false;
    }
    error.textContent = "";
    return true;
}

function validateFeedbackForm() {
    var name = document.getElementById("feedback_name").value.trim();
    var rating = document.getElementById("rating").value;
    var message = document.getElementById("message").value.trim();
    var error = document.getElementById("feedbackError");

    if (name === "" || rating === "" || message === "") {
        error.textContent = "Please complete all feedback fields.";
        return false;
    }
    if (message.length < 10) {
        error.textContent = "Feedback message must be at least 10 characters.";
        return false;
    }
    error.textContent = "";
    return true;
}

function showNotify(message) {
    var box = document.getElementById("notifyBox");
    box.textContent = message + " You earned +10 points.";
    box.style.display = "block";
}

// ── GA goal tracking ───────────────────────────────
function trackGoal(name) {
    if (typeof gtag !== 'undefined') {
        gtag('event', name, { event_category: 'engagement' });
    }
}