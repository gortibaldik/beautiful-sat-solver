<template>
  <section id="Redis Logs">
    <mdb-card class="mb-4">
      <mdb-card-body class="title-class d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          Logs from Redis Worker
        </h4>
      </mdb-card-body>
    </mdb-card>
    <mdb-row>
      <mdb-col md="12">
        <mdb-card class="card-with-logs rounded-border custom-margin-top ">
          <mdb-card-title class="blue darken-2 rounded-border text-center">
            <ul class="list-inline" style="margin-bottom: 0px;">
              <li class="list-inline-item card-header-hoverable"
                @click="switchOnModalStd()">
                <h4 class="h4-responsive text-white spaced-title">Standard Redis Worker Logs</h4>
              </li>
              <li class="header-button-style list-inline-item"
                @click="fetchRedisLogs()">
                <h4 class="h4-responsive text-white">Refresh</h4>
              </li>
            </ul>
          </mdb-card-title>
          <mdb-card-body>
            <div class="scrollbar-class">
              <mdb-scrollbar v-html="stdLogs">
              </mdb-scrollbar>
            </div>
          </mdb-card-body>
        </mdb-card>
      </mdb-col>
    </mdb-row>
    <mdb-row>
      <mdb-col md="12">
        <mdb-card class="card-with-logs rounded-border">
          <mdb-card-title class="blue darken-2 rounded-border text-center">
            <ul class="list-inline" style="margin-bottom: 0px;">
              <li class="list-inline-item card-header-hoverable"
                @click="switchOnModalError()">
                <h4 class="h4-responsive text-white spaced-title">Error Redis Worker Logs</h4>
              </li>
              <li class="header-button-style list-inline-item"
                @click="fetchRedisLogs()">
                <h4 class="h4-responsive text-white">Refresh</h4>
              </li>
            </ul>
          </mdb-card-title>
          <mdb-card-body>
            <div class="scrollbar-class">
              <mdb-scrollbar v-html="errorLogs">
              </mdb-scrollbar>
            </div>
          </mdb-card-body>
        </mdb-card>
      </mdb-col>
    </mdb-row>
    <mdb-modal size="fluid" :show="displayModal" @close="displayModal = false" scrollable>
      <mdb-modal-header>
        <mdb-modal-title>{{modalTitle}}</mdb-modal-title>
      </mdb-modal-header>
      <mdb-modal-body v-html="modalMessage">
      </mdb-modal-body>
      <mdb-modal-footer>
        <mdb-btn color="secondary" @click.native="displayModal = false">Close</mdb-btn>
      </mdb-modal-footer>
    </mdb-modal>
  </section>
</template>

<script>
import { 
  mdbRow,
  mdbCol,
  mdbCard,
  mdbCardTitle,
  mdbCardBody,
  mdbScrollbar,
  mdbModal,
  mdbModalHeader,
  mdbModalFooter,
  mdbModalBody,
  mdbBtn,
  mdbModalTitle,
} from 'mdbvue'

import redis_logs from '@/assets/js/get_redis_logs'

export default {
  name: 'Profile',
  components: {
    mdbRow,
    mdbCol,
    mdbCard,
    mdbCardTitle,
    mdbCardBody,
    mdbScrollbar,
    mdbModal,
    mdbModalHeader,
    mdbModalFooter,
    mdbModalBody,
    mdbBtn,
    mdbModalTitle,
  },
  data () {
    let basicMessage = "<code><strong>Nothing to show</strong></code>"
    return {
      errorLogs: basicMessage,
      stdLogs: basicMessage,
      displayModal: false,
      modalMessage: "",
      modalTitle: "",
    }
  },
  methods: {
    async fetchRedisLogs() {
      let [errorLogs, stdLogs] = await redis_logs.fetch(this.serverAddress)
      this.errorLogs = errorLogs
      this.stdLogs = stdLogs
    },
    switchOnModalError() {
      this.displayModal = true
      this.modalMessage = this.errorLogs
      this.modalTitle = "Error Redis Worker Logs"
    },
    switchOnModalStd() {
      this.displayModal = true
      this.modalMessage = this.stdLogs
      this.modalTitle = "Standard Redis Worker Logs"
    },
  },
  created() {
    this.serverAddress = process.env.VUE_APP_SERVER_ADDRESS
    console.log(`server address: "${this.serverAddress}"`)
    this.fetchRedisLogs()
  }
}
</script>

<style scoped>
.card-with-logs {
  margin-top: 20px;
}

.rounded-border {
  border-radius: 5px;
}

.spaced-title {
  margin: 5px;
}

.card-header-hoverable:hover {
  background-color: #5595fb !important;
}

.scrollbar-class {
  height: 40vh
}

.graph-li-class {
  padding-top:13px;
  height: 50px;
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

.title-class {
  background-color: white;
  padding-left: 20px;
  border-radius: 5px;
}

.custom-margin-top {
  margin-top: 0px
}
</style>
