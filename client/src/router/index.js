import Vue from 'vue';
import Router from 'vue-router';
import Benchmarks from '@/components/Benchmarks'
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