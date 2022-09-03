<template>
  <section id="tables">
    <mdb-card class="mb-4">
      <mdb-card-body class="title-class d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          Results of Past Runs of NQueens Problem
        </h4>
      </mdb-card-body>
    </mdb-card>
    <mdb-row class="results-row">
      <mdb-card cascade narrow class="custom-margin-top border border-0 border-dark">
        <mdb-card-body class="results-table">
          <mdb-scrollbar :style="`height: ${calculatedTableHeight};`" class="border rounded-lg">
            <mdb-tbl class="white-background" autoWidth>
              <mdb-tbl-head class="sticky-top z-depth-2">
                <tr>
                  <th
                  v-for="colHeader in data.columns"
                  :key="colHeader.label"
                  @click="sortRowsByIndex(colHeader.label)"
                  :class="`top-table-header hoverable-table-header h6 text-monospace ${textWrapClass}`">
                  <ul class="list-inline">
                    <li class="list-inline-item">
                      {{getViewportWidth() >= 1200 ? colHeader.label : colHeader.field}}   
                    </li>
                    <li class="list-inline-item" style="margin-left: 0.25rem">
                      <mdb-icon icon="sort" fas size="sm" class="red-color" />
                    </li>
                  </ul>
                  </th>
                  <th class="orange-background"/>
                  <th class="h6 text-monospace top-table-header orange-background">
                    <ul class="list-inline">
                      <li class="list-inline-item">
                        Select for Graph
                      </li>
                    </ul>
                  </th>
                </tr>
                <tr>
                  <th v-for="(colHeader, index) in data.columns"
                    :key="index"
                    class="orange-background quarter-padding">
                    <select
                      v-if="uniques[index] != null"
                      class="browser-default custom-select h6-responsive text-monospace hoverable-table-header"
                      v-model="selected_values[colHeader.label]"
                      v-on:change="filterRows()">
                      <option
                        v-for="(val, indexUniques) in uniques[index]"
                        :key="indexUniques"
                        class="text-monospace">{{val}}</option>
                    </select>
                  </th>
                  <th class="orange-background"/>
                  <th class="h6 text-monospace hoverable-table-button dark-blue-color"
                    @click="checkAll()">
                    <ul class="list-inline" style="margin-bottom: 0;">
                      <li class="list-inline-item">
                        {{(no_checked !== 0) ? 'Unselect All' : 'Select All'}}
                      </li>
                    </ul>
                  </th>
                </tr>
              </mdb-tbl-head>
              <mdb-tbl-body>
                <tr v-for="(row, index) in filtered_rows" :key="index">
                  <td
                    v-for="(colHeader, indexC) in data.columns"
                    :key="indexC"
                    :class="`text-monospace dark-blue-color ${canBePressedClass(colHeader)}`"
                    @click="colHeader.can_be_pressed ? showLogFile(index) : () => {}"
                  >{{tableDataContent(colHeader,row)}}</td>
                  <td
                    class="text-monospace dark-blue-color can-be-pressed"
                    @click="deleteLogFile(index)"
                  >
                    Delete
                  </td>
                  <td>
                    <div class="input_wrapper">
                      <input type="checkbox" class="switch_4" @change="checkCheckbox(index)" :checked="row.checked === 'is_checked'">
                    </div>
                  </td>
                  <mdb-modal size="fluid" :show="displayed_modals[index]" @close="closeModal(index)" scrollable>
                    <mdb-modal-header>
                      <mdb-modal-title>Algorithm result</mdb-modal-title>
                    </mdb-modal-header>
                    <mdb-modal-body v-html="modal_messages[index]">
                    </mdb-modal-body>
                    <mdb-modal-footer>
                      <mdb-btn color="secondary" @click.native="closeModal(index)">Close</mdb-btn>
                    </mdb-modal-footer>
                  </mdb-modal>
                </tr>
              </mdb-tbl-body>
            </mdb-tbl>
          </mdb-scrollbar>
        </mdb-card-body>
      </mdb-card>
    </mdb-row>
    <mdb-row>
      <mdb-col md="12">
        <mdb-card cascade narrow class="mt-5 border border-0 border-dark">
          <mdb-view class="gradient-card-header blue darken-2" style="padding: 0;">
            <ul class="list-inline" style="margin-bottom: 0px;">
              <li class="graph-li-class list-inline-item">
                <h4 class="h4-responsive text-white">Data Visualization</h4>
              </li>
              <li class="header-button-style list-inline-item dark-blue-background-hoverable"
                @click="toggleGraphCreation()">
                <h4 class="h4-responsive text-white">Compute from Selected</h4>
              </li>
              <li class="header-button-style list-inline-item dark-blue-background-hoverable"
                @click="downloadCsv()"
              >
                <h4 class="h4-responsive text-white">Download .csv</h4>
              </li>
            </ul>
          </mdb-view>
        </mdb-card>
      </mdb-col>
    </mdb-row>
    <section v-if="showBarChart">
      <mdb-row>
        <mdb-col md="12">
          <mdb-card cascade narrow class="mt-5 border border-0 border-dark">
            <mdb-card-title class="gradient-card-header blue darken-2 rounded-border">
              <h4 class="h4-responsive text-white spaced-title text-center">
                Cumulative data
              </h4>
            </mdb-card-title>
            <mdb-card-body>
              <mdb-horizontal-bar-chart
                :data="barChartData"
                :options="barChartOptions"
                :style="`height: ${barChartHeight}px`">
              </mdb-horizontal-bar-chart>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
      <mdb-row v-for="(visualization, ix) in visualizations" :key="ix">
        <mdb-col md="12">
          <mdb-card cascade narrow class="mt-5 border border-0 border-dark">
            <mdb-card-title class="gradient-card-header blue darken-2 rounded-border">
              <h4 class="h4-responsive text-white spaced-title text-center">
                {{visualization.title}}
              </h4>
            </mdb-card-title>
            <mdb-card-body>
              <mdb-line-chart
                :data="visualization.data"
                :options="lineChartOptions">
              </mdb-line-chart>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
    </section>
  </section>
</template>

<script src="@/assets/js/nqueens_results.js" />
<style scoped src="@/assets/styles/results.css" />