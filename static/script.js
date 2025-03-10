document.querySelector("form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const url = document.getElementById("url").value;
    const expiryDate = document.getElementById("expiry-date").value;

    const response = await fetch("/shorten", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, expiry_date: expiryDate }),
    });

    const result = await response.json();
    if (response.ok) {
        alert("🔗 קישור מקוצר: " + result.short_url);
    } else {
        alert("❌ שגיאה: " + result.error);
    }
});