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
                @click="removeStdRedisLogs()">
                <h4 class="h4-responsive text-white">Clear</h4>
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
                @click="removeErrorRedisLogs()">
                <h4 class="h4-responsive text-white">Clear</h4>
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

<script src='@/assets/js/redis_logs' />
<style scoped src='@/assets/styles/redis_logs.css' />
