document.querySelector("form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const url = document.getElementById("url").value;
    const expiryDate = document.getElementById("expiry-date").value;

    const response = await fetch("/shorten", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            url: url, 
            expiry_date: expiryDate }),
    });

    const result = await response.json();
    if (response.ok) {
        alert("🔗 קישור מקוצר: " + result.short_url);
    } else {
        alert("❌ שגיאה: " + result.error);
    }
});

window.onload = function() {
    const today = new Date().toISOString().split('T')[0];
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 7);
    const maxDateString = maxDate.toISOString().split('T')[0];

    const expiryDateInput = document.getElementById("expiry-date");
    expiryDateInput.setAttribute("min", today);
    expiryDateInput.setAttribute("max", maxDateString);
};