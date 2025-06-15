document.addEventListener('DOMContentLoaded', async () => {
    const paymentsTableBody = document.getElementById('payments-table-body');
    const noPaymentsMessage = document.getElementById('no-payments-message');

    try {
        const response = await fetch('http://localhost:5003/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: `
                    query {
                        allPayments {
                            id
                            customer
                            amount
                            status
                            date
                        }
                    }
                `
            }),
        });

        const result = await response.json();
        console.log('Payment Service GraphQL Response:', result);

        if (result.data && result.data.allPayments && result.data.allPayments.length > 0) {
            result.data.allPayments.forEach(payment => {
                const row = paymentsTableBody.insertRow();
                row.insertCell().textContent = payment.id;
                row.insertCell().textContent = payment.customer;
                row.insertCell().textContent = `Rp ${Number(payment.amount).toLocaleString('id-ID', {minimumFractionDigits: 0})}`;
                
                const statusCell = row.insertCell();
                const statusBadge = document.createElement('span');
                statusBadge.classList.add('badge');
                if (payment.status === 'completed') {
                    statusBadge.classList.add('bg-success');
                } else if (payment.status === 'pending') {
                    statusBadge.classList.add('bg-warning', 'text-dark');
                } else if (payment.status === 'failed') {
                    statusBadge.classList.add('bg-danger');
                }
                statusBadge.textContent = payment.status.toLowerCase();
                statusCell.appendChild(statusBadge);

                const dateCell = row.insertCell();
                dateCell.textContent = new Date(payment.date).toLocaleString();

                // Tombol Tracking
                const trackingBtn = document.createElement('button');
                trackingBtn.textContent = 'Tracking';
                trackingBtn.classList.add('btn', 'btn-info', 'btn-sm', 'ms-2');
                trackingBtn.onclick = async () => {
                    // Kirim data ke Delivery Service
                    await fetch('http://localhost:5004', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            payment_id: payment.id,
                            customer: payment.customer,
                            amount: payment.amount,
                            date: payment.date
                        })
                    });
                    alert('Pesanan dikirim ke Delivery Service!');
                    // window.location.href = 'http://localhost:5004'; // Optional redirect
                };
                dateCell.appendChild(trackingBtn);

                // Tambahkan tombol Bayar jika status pending
                if (payment.status === 'pending') {
                    const actionCell = row.insertCell();
                    const payButton = document.createElement('button');
                    payButton.textContent = 'Bayar';
                    payButton.classList.add('btn', 'btn-success', 'btn-sm');
                    payButton.onclick = async () => {
                        await fetch('http://localhost:5003/graphql', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                query: `mutation { updatePaymentStatus(id: ${payment.id}, status: \"completed\") { payment { id status } } }`
                            })
                        });
                        alert('Pembayaran berhasil!');
                        window.location.reload();
                    };
                    actionCell.appendChild(payButton);
                } else {
                    row.insertCell(); // Empty cell for non-pending payments
                }
            });
        } else {
            noPaymentsMessage.style.display = 'block';
        }
    } catch (error) {
        console.error('Error fetching payments:', error);
        noPaymentsMessage.textContent = 'Gagal memuat pembayaran. Terjadi kesalahan.';
        noPaymentsMessage.style.display = 'block';
    }
}); 