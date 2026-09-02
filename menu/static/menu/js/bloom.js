document.addEventListener("DOMContentLoaded", function () {

    const interactiveElements = document.querySelectorAll(
        "a, button, input, select"
    );

    interactiveElements.forEach(function (element) {

        element.addEventListener("click", function () {

            element.classList.remove("qd-bloom");

            // Restart animation
            void element.offsetWidth;

            element.classList.add("qd-bloom");

            setTimeout(function () {
                element.classList.remove("qd-bloom");
            }, 600);

        });

    });

});