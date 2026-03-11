const btnLogin = document.getElementById("btnLogin");

if(btnLogin){
    btnLogin.addEventListener("click", async () => {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try{
        const response = await fetch("http://localhost:5000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        
        if (data.success) {
            localStorage.setItem("token", data.token);
            window.location.href = "/"; //Llevar a index
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error("Error:", error);
    }
});
}


