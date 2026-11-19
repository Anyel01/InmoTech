
document.addEventListener('DOMContentLoaded', () => {
    
    const alertCloseButtons = document.querySelectorAll('.alert-close');
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', () => {
            const alertElement = button.closest('.alert');
            if (alertElement) {
                alertElement.style.opacity = '0';
                setTimeout(() => alertElement.remove(), 250);
            }
        });
    });

  
    const departamentoSelect = document.getElementById('id_departamento');
    const ciudadSelect = document.getElementById('id_ciudad');

    if (departamentoSelect && ciudadSelect) {
        departamentoSelect.addEventListener('change', async (e) => {
            const deptoId = e.target.value;
            ciudadSelect.innerHTML = '<option value="">Cargando ciudades...</option>';
            ciudadSelect.disabled = true;

            if (!deptoId) {
                ciudadSelect.innerHTML = '<option value="">-- Primero seleccione departamento --</option>';
                return;
            }

            try {
                const response = await fetch(`/api/ciudades/${deptoId}`);
                if (!response.ok) throw new Error('Error al cargar ciudades');
                const ciudades = await response.json();

                ciudadSelect.innerHTML = '<option value="">-- Seleccione una ciudad --</option>';
                ciudades.forEach(c => {
                    const option = document.createElement('option');
                    option.value = c.id_ciudad;
                    option.textContent = c.nombre;
                    ciudadSelect.appendChild(option);
                });
                ciudadSelect.disabled = false;
            } catch (err) {
                console.error(err);
                ciudadSelect.innerHTML = '<option value="">Error al cargar ciudades</option>';
            }
        });
    }

    
    const registerForm = document.getElementById('form-registro');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const pass = document.getElementById('password')?.value;
            const confirmPass = document.getElementById('confirm_password')?.value;

            if (pass && confirmPass && pass !== confirmPass) {
                e.preventDefault();
                alert('Las contraseñas no coinciden. Por favor verifíquelas.');
            }
        });
    }

   
    const visitDateInput = document.getElementById('fecha_visita');
    if (visitDateInput) {
        const now = new Date();
        now.setHours(now.getHours() + 1);
        const pad = value => String(value).padStart(2, '0');
        visitDateInput.min = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
    }


    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const message = form.getAttribute('data-confirm') || '¿Está seguro de realizar esta acción?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
});
