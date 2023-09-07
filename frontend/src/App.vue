<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import 'toastify-js/src/toastify.css';
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
const host = location.hostname;

const ocrText = (file: File) => {
  list.splice(0);
  const formData = new FormData();
  formData.append('file', file);
  maskVisible.value = true;
  axios
    .post(`http://${host}:8000/ocr/text?time=${+new Date()}`, formData)
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
        // setTimeout(() => {
        //   updateTextFontSize();
        // }, 3000);
      }
    })
    .catch(function (error: any) {
      console.log(error);
    })
    .finally(() => {
      maskVisible.value = false;
    });
};

// function updateTextFontSize() {
//   let listEl: any = document.getElementsByClassName('text-item');
//   for (let index = 0; index < listEl.length; index++) {
//     const domContainer = listEl[index];
//     let domText = domContainer.querySelector('.text');
//     if (domText.clientWidth <= domContainer.clientWidth) {
//       domText.style.transform = 'none';
//     } else {
//       let r = domContainer.clientWidth / domText.clientWidth;
//       domText.style.transform = 'scale(' + r + ')';
//     }
//   }
// };

const currentContent = ref('');
const selectText = (item: TextItem) => {
  currentContent.value = item.content;
};

const copy = (text: string) => {
  var input = document.createElement('input');
  input.setAttribute('value', text);
  document.body.appendChild(input);
  input.select();
  var result = document.execCommand('copy');
  document.body.removeChild(input);
  notifyMe();
  return result;
};

const maskVisible = ref(false);

function notifyMe() {
  Toastify({
    text: '操作成功',
    duration: 3000,
    newWindow: true,
    gravity: 'top', // `top` or `bottom`
    position: 'center', // `left`, `center` or `right`
    stopOnFocus: true, // Prevents dismissing of toast on hover
    style: {
      background: 'rgba(0,0,0,0.5)',
    },
  }).showToast();
  // want to be respectful there is no need to bother them anymore.
}
</script>

<template>
  <div class="container">
    <div class="mask" v-show="maskVisible">
      <span>正在识别,请等待...</span>
    </div>
    <div class="img-box flex-1">
      <div
        class="text-item"
        v-for="item in list"
        @click="selectText(item)"
        :style="{ top: item.top, left: item.left, width: item.width, height: item.height, lineHeight: item.height }"
      >
        <!-- <div class="text">{{ item.content }}</div> -->
      </div>
      <img id="img" src="" alt="" srcset="" />
    </div>
    <input type="file" name="" id="upload-file" @change="changeFile" style="visibility: hidden; position: absolute" />
    <div class="bottom-box">
      <div class="header-box">
        <label for="upload-file" style="cursor: pointer; color: blue">选择图片</label>

        <label style="cursor: pointer; color: blue" @click="copy(currentContent)">复制</label>
      </div>
      <textarea
        name=""
        id=""
        cols="30"
        rows="10"
        v-model="currentContent"
        style="margin-top: 32px; width: 100%"
      ></textarea>
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
.mask {
  position: fixed;
  width: 100vw;
  height: 100vh;
  opacity: 0.6;
  z-index: 9999;
  background-color: #000;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 3rem;
}
.img-box {
  position: relative;
  overflow: auto;
  padding-bottom: 296px;
}
.img-box img {
  width: 100%;
  height: auto;
}

.text-item {
  cursor: pointer;
  position: absolute;
  border: 1px solid red;
  background-color: transparent;
  font-size: 12px;
  z-index: 99;
}

.text-item .text {
  display: inline-block;
  color: #000;
  white-space: nowrap;
  transform-origin: left center;
}

.bottom-box {
  position: fixed;
  z-index: 999;
  bottom: 0;
  left: 0;
  right: 0;
  border-top: 1px solid #f0f0f0;
  background-color: #fff;
  padding: 20px;
}
.header-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

textarea {
  width: calc(100vw - 40px);
}
</style>
