document.addEventListener('DOMContentLoaded', function () {
    const reInput = document.getElementById('id_re');
    if (!reInput) return;

    reInput.setAttribute('maxlength', '9');
    reInput.setAttribute('placeholder', '000.000-0');

    reInput.addEventListener('input', function (e) {
        let v = e.target.value.toUpperCase().replace(/[^0-9A-Z]/g, '').slice(0, 7);
        if (v.length > 6) {
            v = v.slice(0, 3) + '.' + v.slice(3, 6) + '-' + v.slice(6);
        } else if (v.length > 3) {
            v = v.slice(0, 3) + '.' + v.slice(3);
        }
        e.target.value = v;
    });
});