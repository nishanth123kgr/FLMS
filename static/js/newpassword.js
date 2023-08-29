
        // Get references to the input fields, the submit button, and the paragraph where we'll display the message.
        const password1Input = document.getElementById("password1");
        const password2Input = document.getElementById("password2");
        const passwordMatchMessage = document.getElementById("passwordMatch");
        const submitButton = document.getElementById("submitButton");

        // Add input event listeners to both password fields.
        password1Input.addEventListener("input", checkPasswordMatch);
        password2Input.addEventListener("input", checkPasswordMatch);

        // Function to check if the passwords match and enable/disable the submit button.
        function checkPasswordMatch() {
            const password1 = password1Input.value;
            const password2 = password2Input.value;

            // Check if both fields are empty, and if they are, disable the submit button.
            if (password1 === '' && password2 === '') {
                passwordMatchMessage.style.color = "black";
                passwordMatchMessage.textContent = "";
                submitButton.disabled = true;
            } else if (password1 === password2) {
                passwordMatchMessage.style.color = "green";
                passwordMatchMessage.textContent = "Passwords match!";
                submitButton.disabled = false;
            } else {
                passwordMatchMessage.style.color = "red";
                passwordMatchMessage.textContent = "Passwords do not match!";
                submitButton.disabled = true;
            }
        }