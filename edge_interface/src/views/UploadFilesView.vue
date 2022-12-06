<template>
  <div class="container" style="width:600px">
    <div style="margin: 20px">
      <h3>Launch an item</h3>
      <h4>Upload the needed files to get a decision</h4>
    </div>

    <upload-files></upload-files>
  </div>
</template>

<script>
import UploadFiles from "@/components/UploadFiles";

export default {
  name: "item-upload",
  components: {
    UploadFiles
  }
};
</script>
