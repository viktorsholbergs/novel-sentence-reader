document.getElementById("novelForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent default form submission

    const formData = new FormData(this);

    fetch("/add_novel", {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            // Wait 2 seconds before reloading the page
            setTimeout(() => {
                window.location.reload();
            }, 3000);  // 2000 milliseconds = 2 seconds
        } else {
            alert("Error adding novel.");
        }
    }).catch(error => {
        console.error("Error:", error);
        alert("Something went wrong.");
    });
});