import Vue from 'vue';
import Router from 'vue-router';
import Benchmarks from '@/components/Benchmarks'
import Results from '@/components/Results'
import BadGateway from '@/components/BadGateway'


Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/benchmarks',
      name: 'Benchmarks',
      component: Benchmarks,
      props: { page: 1 },
      alias: '/'
    },
    {
      path: '/results',
      name: 'Results',
      component: Results,
      props: { page: 2 }
    },
    {
      path: '/404',
      name: 'BadGateway',
      props: { page: 5 },
      component: BadGateway
    },
    {
      path: '*',
      props: { page: 5 },
      redirect: '/404'
    }
  ]
})