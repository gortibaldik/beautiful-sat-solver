<template>
<section>
  <mdb-card class="rounded-border">
    <mdb-card-title class="blue darken-2 rounded-border text-center">
      <li class="list-inline-item card-header-hoverable"
        @click="switchOnModal()">
        <h4 class="h4-responsive text-white spaced-title">{{title}}</h4>
      </li>
      <li v-if="clearPossibility" class="header-button-style list-inline-item"
        @click="clearFunction()">
        <h4 class="h4-responsive text-white">Clear</h4>
      </li>
    </mdb-card-title>
    <mdb-card-body>
      <div class="scrollbar-class">
        <mdb-scrollbar v-html="message.data">
        </mdb-scrollbar>
      </div>
    </mdb-card-body>
  </mdb-card>
  <mdb-modal size="fluid" :show="displayModal" @close="displayModal = false" scrollable>
    <mdb-modal-header>
      <mdb-modal-title>{{title}}</mdb-modal-title>
    </mdb-modal-header>
    <mdb-modal-body v-html="message.data">
    </mdb-modal-body>
    <mdb-modal-footer>
      <mdb-btn color="secondary" @click.native="displayModal = false">Close</mdb-btn>
    </mdb-modal-footer>
  </mdb-modal>
</section>
</template>
<script>
import {
  mdbCard,
  mdbCardBody,
  mdbCardTitle,
  mdbScrollbar,
  mdbModal,
  mdbModalHeader,
  mdbModalFooter,
  mdbModalBody,
  mdbBtn,
  mdbModalTitle,
} from 'mdbvue'
export default {
  name: 'modal-card',
  components: {
    mdbCard,
    mdbCardBody,
    mdbCardTitle,
    mdbScrollbar,
    mdbModal,
    mdbModalHeader,
    mdbModalFooter,
    mdbModalBody,
    mdbBtn,
    mdbModalTitle,
  },
  props: [
    'message',
    'title',
    'clearPossibility',
    'clearFunction'
  ],
  data() {
    return {
      displayModal: false,
    }
  },
  methods: {
    switchOnModal() {
      this.displayModal = true
    }
  }
}
</script>
<style scoped>

.card-header-hoverable:hover {
  background-color: #5595fb !important;
}

.spaced-title {
  margin: 5px;
}

.scrollbar-class {
  height: 25vh;
}

.header-button-style {
  float: right;
  padding: 5px;
  height: 50px;
  border-style: solid;
  border-color: black;
  border-width: thin;
  background-color: #1452b6; 
}

.header-button-style:hover {
  background-color: #5595fb
}
</style>
