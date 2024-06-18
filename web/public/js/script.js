// Show loading process button when the form is submitted
document.getElementById('form-upload').addEventListener('submit', () => {
    var btnProcess = document.getElementById('button-process');
    var btnProcessText = btnProcess.querySelector('.button-text');
    var loader = btnProcess.querySelector('.loader');

    btnProcessText.classList.add('hidden');
    loader.classList.remove('hidden');

    btnProcess.setAttribute('disabled', true);
});
