document.getElementById("novelForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent default form submission

    const formData = new FormData(this);

    fetch("/add_novel", {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            // Wait 3 seconds before reloading the page
            setTimeout(() => {
                window.location.reload();
            }, 3000);  
        } else {
            alert("Error adding novel.");
        }
    }).catch(error => {
        console.error("Error:", error);
        alert("Something went wrong.");
    });
});