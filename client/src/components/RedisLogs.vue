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
        <modal-card
          :message="stdLogs"
          title="Standard Redis Worker Logs"
          :clearPossibility="true"
          :clearFunction="removeStdRedisLogsBinded"
        />
      </mdb-col>
    </mdb-row>
    <mdb-row class="custom-margin-top">
      <mdb-col md="12">
        <modal-card
          :message="errorLogs"
          title="Error Redis Worker Logs"
          :clearPossibility="true"
          :clearFunction="removeErrorRedisLogsBinded"
        />
      </mdb-col>
    </mdb-row>
  </section>
</template>

<script src='@/assets/js/redis_logs' />
<style scoped src='@/assets/styles/redis_logs.css' />
