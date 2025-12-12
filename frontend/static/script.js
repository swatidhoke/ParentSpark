
document.addEventListener("DOMContentLoaded", () => {
    console.log("inside a addEventListener function");     
    const aiBtn = document.getElementById("generateRecommendationBtn");
    console.log("clicking generateRecommendationBtn function" + aiBtn.textContent);  
    aiBtn.addEventListener("click", async () => {
        const message = document.getElementById("FeedbackMessage").value.trim();
        if (!message) return alert("Please write some feedback first.");
        const formData = new FormData();
        formData.append("message", message);

        try {
            const response = await fetch("/feedback_suggestion", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            console.log("AI Suggestion: " + data.suggestion);
        } catch (err) {
            console.error(err);
            alert("Failed to get AI suggestion");
        }
    });
});
