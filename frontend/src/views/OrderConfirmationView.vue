<template>
  <div class="confirmation-page">
    <div class="confirmation-box">
      <div class="icon-success">✓</div>
      <h1>Thank You For Your Order!</h1>
      <p>
        Your order has been placed successfully. We will notify you via email
        once it has shipped.
      </p>
      <div class="order-details">
        <strong>Order ID:</strong> #{{ $route.params.orderId }}
      </div>
      <router-link to="/my-designs" class="cta-button"
        >View My Designs</router-link
      >
    </div>
  </div>
</template>

<script>
export default {
  name: "OrderConfirmationView",
};
</script>

<style scoped>
.confirmation-page {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 50px 20px;
  min-height: 80vh;
}
.confirmation-box {
  max-width: 600px;
}
.icon-success {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: #28a745;
  color: white;
  font-size: 3rem;
  line-height: 80px;
  margin: 0 auto 30px;
}
h1 {
  font-size: 2.2rem;
  margin-bottom: 15px;
}
p {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin-bottom: 30px;
}
.order-details {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 30px;
}
.cta-button {
  background-color: #fc4c02;
  color: white;
  padding: 12px 25px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.2s;
}
.cta-button:hover {
  background-color: #e24300;
}
</style>
