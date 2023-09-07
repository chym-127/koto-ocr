<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import axios from 'axios';

let fileInputEl: HTMLInputElement | null = null;
let scale = 1;
let currentFile: File | null = null;
onMounted(() => {
  fileInputEl = document.getElementById('upload-file') as HTMLInputElement;
});
const changeFile = () => {
  if (fileInputEl?.files?.length) {
    currentFile = fileInputEl.files[0];
    fileInputEl!.value = '';
    let fr = new FileReader();
    fr.onload = function () {
      let imgEl: HTMLImageElement | null = document.getElementById('img') as HTMLImageElement;
      imgEl!.src = fr.result as string;

      var img = new Image();
      img.onload = function () {
        let imgDom = document.querySelector('#img');
        scale = imgDom!.clientWidth / img.width;
        ocrText(currentFile!);
      };
      img.src = fr.result as string;
    };
    fr.readAsDataURL(currentFile);
  }
};

interface TextItem {
  content: string;
  top: string;
  left: string;
  height: string;
  width: string;
}

const list = reactive<TextItem[]>([]);

const ocrText = (file: File) => {
  list.splice(0);
  const formData = new FormData();
  formData.append('file', file);
  axios
    .post(`http://127.0.0.1:8000/ocr/text?time=${+new Date()}`, formData)
    .then(function (response: any) {
      if (response.data?.data?.length) {
        response.data.data.forEach((item: any) => {
          let textItem: TextItem = {
            content: item.content,
            top: item.rect[0][1] * scale + 'px',
            left: item.rect[0][0] * scale + 'px',
            height: (item.rect[3][1] - item.rect[0][1]) * scale + 'px',
            width: item.rect[1][0] * scale - item.rect[0][0] * scale + 'px',
          };
          list.push(textItem);
        });
        setTimeout(() => {
          updateTextFontSize();
        }, 3000);
      }
    })
    .catch(function (error: any) {
      console.log(error);
    });
};

const updateTextFontSize = () => {
  let listEl: any = document.getElementsByClassName('text-item');
  for (let index = 0; index < listEl.length; index++) {
    const domContainer = listEl[index];
    let domText = domContainer.querySelector('.text');
    if (domText.clientWidth <= domContainer.clientWidth) {
      domText.style.transform = 'none';
    } else {
      let r = domContainer.clientWidth / domText.clientWidth;
      domText.style.transform = 'scale(' + r + ')';
    }
  }
};

const currentContent = ref('');
const selectText = (item: TextItem) => {
  currentContent.value = item.content;
};
</script>

<template>
  <div class="container">
    <div class="img-box flex-1">
      <div
        class="text-item"
        v-for="item in list"
        @click="selectText(item)"
        :style="{ top: item.top, left: item.left, width: item.width, height: item.height, lineHeight: item.height }"
      >
        <div class="text">{{ item.content }}</div>
      </div>
      <img id="img" src="" alt="" srcset="" />
    </div>
    <div style="width: 300px; height: 100%; padding: 20px;box-sizing: border-box;">
      <input type="file" name="" id="upload-file" @change="changeFile" />
      <textarea name="" id="" cols="30" rows="10" v-model="currentContent" style="margin-top: 32px"></textarea>
    </div>
  </div>
</template>

<style scoped>
.container {
  box-sizing: border-box;
  width: 100vw;
  height: 100vh;
  overflow: auto;
  display: flex;
  align-items: center;
}
.flex-1 {
  flex: 1;
  height: 100%;
  box-sizing: border-box;
}
.img-box {
  position: relative;
  overflow: auto;
}
.img-box img {
  width: 100%;
  height: auto;
}

.text-item {
  cursor: pointer;
  position: absolute;
  border: 1px solid red;
  background-color: #fff;
  font-size: 12px;
  opacity: 0;
  z-index: 99;
}

.text-item .text {
  display: inline-block;
  color: #000;
  white-space: nowrap;
  transform-origin: left center;
}
</style>
