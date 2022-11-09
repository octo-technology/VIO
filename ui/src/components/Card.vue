<template>
  <div class="card">
    <h1>{{ item._id }}</h1>
    <h2>{{ item.serial_number }}</h2>
    <h2>{{ item.category }}</h2>
    <h2>{{ item.received_time }}</h2>
    <h2>{{ item.decision }}</h2>
  </div>
</template>

<script>
export default {
  name: "card",
  props: ["item"]
};
</script>

<style lang="scss" scoped>
.card {
  display: flex;
  flex-flow: column wrap;
  align-items: flex-start;
  color: black;

  width: 80vw;
  max-width: 500px;
  border: 1px solid #c9c9c9;
  margin: 10px 20px;
  padding: 10px;
  border-radius: 3px;

  & p {
    font-size: 10px;
  }

  & h1 {
    font-weight: bold;
    font-size: 20px;
  }

  & h2 {
    font-size: 15px;
  }

  &-title {
    font-weight: bold;
    margin-bottom: 5px;
  }

  &:hover {
    transition: all 0.1s ease;
    transform: scale(1.05);
  }
}
</style>
