


    document.addEventListener('DOMContentLoaded', function() {
        const paymentMethodSelect = document.getElementById('paymentMethod'); // Replace with the correct ID
        const paymentProofGroup = document.getElementById('paymentProofGroup'); // Replace with the correct ID
    
        paymentMethodSelect.addEventListener('change', function() {
            if (paymentMethodSelect.value === 'check' || paymentMethodSelect.value === 'other') {
                paymentProofGroup.style.display = 'block';
            } else {
                paymentProofGroup.style.display = 'none';
            }
        });
    });

