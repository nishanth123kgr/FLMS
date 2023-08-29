const inputs = document.querySelectorAll(".otp-field > input");
const button = document.querySelector(".btn");

window.addEventListener("load", () => inputs[0].focus());
button.setAttribute("disabled", "disabled");

inputs[0].addEventListener("paste", function (event) {
  event.preventDefault();

  const pastedValue = (event.clipboardData || window.clipboardData).getData(
    "text"
  );
  const otpLength = inputs.length;

  for (let i = 0; i < otpLength; i++) {
    if (i < pastedValue.length) {
      inputs[i].value = pastedValue[i];
      inputs[i].removeAttribute("disabled");
      inputs[i].focus;
    } else {
      inputs[i].value = ""; // Clear any remaining inputs
      inputs[i].focus;
    }
  }
});

inputs.forEach((input, index1) => {
  input.addEventListener("keyup", (e) => {
    const currentInput = input;
    const nextInput = input.nextElementSibling;
    const prevInput = input.previousElementSibling;

    if (currentInput.value.length > 1) {
      currentInput.value = "";
      return;
    }

    if (
      nextInput &&
      nextInput.hasAttribute("disabled") &&
      currentInput.value !== ""
    ) {
      nextInput.removeAttribute("disabled");
      nextInput.focus();
    }

    if (e.key === "Backspace") {
      inputs.forEach((input, index2) => {
        if (index1 <= index2 && prevInput) {
          input.setAttribute("disabled", true);
          input.value = "";
          prevInput.focus();
        }
      });
    }

    button.classList.remove("active");
    button.setAttribute("disabled", "disabled");

    const inputsNo = inputs.length;
    if (!inputs[inputsNo - 1].disabled && inputs[inputsNo - 1].value !== "") {
      button.classList.add("active");
      button.removeAttribute("disabled");

      return;
    }
  });
});

function reloadPage() {
  // Use the location.reload() method to reload the page
  location.reload();
}

function combineAndSubmit() {
  // Get all input values
  const digit1 = document.querySelector('input[name="digit1"]').value;
  const digit2 = document.querySelector('input[name="digit2"]').value;
  const digit3 = document.querySelector('input[name="digit3"]').value;
  const digit4 = document.querySelector('input[name="digit4"]').value;
  const digit5 = document.querySelector('input[name="digit5"]').value;
  const digit6 = document.querySelector('input[name="digit6"]').value;

  // Combine the values
  const combinedValue = digit1 + digit2 + digit3 + digit4 + digit5 + digit6;

  // Set the combined value to a hidden input field
  const hiddenInput = document.createElement('input');
  hiddenInput.type = 'hidden';
  hiddenInput.name = 'combinedValue';
  hiddenInput.value = combinedValue;

  // Append the hidden input to the form
  const otpForm = document.getElementById('otpForm');
  otpForm.appendChild(hiddenInput);

  // Submit the form
  otpForm.submit();

}