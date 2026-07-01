console.log("Dashboard Loaded");

// Bootstrap tooltips
document.addEventListener("DOMContentLoaded", function () {

    // Button hover animation
    const buttons = document.querySelectorAll(".btn");

    buttons.forEach(btn => {

        btn.addEventListener("mouseenter", function () {
            this.style.transform = "scale(1.05)";
            this.style.transition = "0.3s";
        });

        btn.addEventListener("mouseleave", function () {
            this.style.transform = "scale(1)";
        });

    });

    // Card hover effect
    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {

        card.addEventListener("mouseenter", function () {
            this.style.boxShadow = "0px 10px 25px rgba(0,0,0,0.2)";
            this.style.transition = "0.3s";
        });

        card.addEventListener("mouseleave", function () {
            this.style.boxShadow = "";
        });

    });

});
