<template>
  <transition name="modal-fade">
    <div v-if="visible" class="modal-backdrop" @click.self="$emit('cancel')">
      <div class="modal-content">
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-message">{{ message }}</p>
        <div class="modal-actions">
          <button @click="$emit('cancel')" class="button-secondary">
            Cancel
          </button>
          <button @click="$emit('confirm')" class="button-danger">
            Confirm
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: "ModalComponent",
  props: {
    visible: Boolean,
    title: String,
    message: String,
  },
};
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 90%;
  max-width: 450px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
}
.modal-title {
  margin-top: 0;
  font-size: 1.5rem;
}
.modal-message {
  margin-bottom: 25px;
  line-height: 1.6;
  color: #555;
}
.modal-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}
.modal-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
.button-secondary {
  background-color: #f0f2f5;
}
.button-danger {
  background-color: #dc3545;
  color: white;
}
</style>
