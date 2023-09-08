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
  rotate?: string;
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
          let width =
            getDistanceBetweenTwoPoints(item.rect[1][0], item.rect[1][1], item.rect[0][0], item.rect[0][1]) * scale;
          let rotate = 'rotate(0deg)';
          if (item.rect[0][1] !== item.rect[1][1]) {
            rotate = `rotate(${calAngle(
              [item.rect[0][1], 1],
              [item.rect[1][0] - item.rect[0][0], item.rect[1][1] - item.rect[0][1]]
            )}deg)`;
          }
          let textItem: TextItem = {
            content: item.content,
            top: item.rect[0][1] * scale + 'px',
            left: item.rect[0][0] * scale + 'px',
            height: (item.rect[3][1] - item.rect[0][1]) * scale + 'px',
            rotate: rotate,
            width: width + 'px',
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

function getDistanceBetweenTwoPoints(x1: number, y1: number, x2: number, y2: number) {
  var a = x1 - x2;
  var b = y1 - y2;
  var result = Math.sqrt(Math.pow(a, 2) + Math.pow(b, 2));
  return result;
}

function calCos(a: Array<number>, b: Array<number>) {
  // 点积
  let dotProduct = a[0] * b[0] + a[1] * b[1];
  let d = Math.sqrt(a[0] * a[0] + a[1] * a[1]) * Math.sqrt(b[0] * b[0] + b[1] * b[1]);
  return dotProduct / d;
}

function calAngle(a: Array<number>, b: Array<number>) {
  const radian = calCos(a, b);
  let angle = (Math.acos(radian) * 180) / Math.PI;
  if (a[0] > b[1]) {
    angle = -angle;
  }
  return angle;
}

console.log(calAngle([816, 1], [775, 527]));

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
  if (mode.value) {
    currentContent.value += item.content + '\n';
  } else {
    currentContent.value = item.content;
  }
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

const mode = ref(false);
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
        :style="{
          top: item.top,
          left: item.left,
          width: item.width,
          height: item.height,
          lineHeight: item.height,
          transform: item.rotate,
          background: mode ? '#fff' : 'transparent',
        }"
      >
        <div class="text" v-if="mode">{{ item.content }}</div>
      </div>
      <img id="img" src="" alt="" srcset="" />
    </div>
    <input type="file" name="" id="upload-file" @change="changeFile" style="visibility: hidden; position: absolute" />
    <div class="bottom-box">
      <div class="header-box">
        <label for="upload-file" style="cursor: pointer; color: blue">选择图片</label>
        <div>
          <label style="cursor: pointer; color: blue; margin-right: 12px" @click="mode = !mode">
            {{ mode ? '选择模式' : '普通模式' }}
          </label>
          <label style="cursor: pointer; color: blue" @click="copy(currentContent)">复制</label>
        </div>
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
  font-size: 2rem;
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
  font-size: 12px;
  z-index: 99;
  transform-origin: top left;
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
