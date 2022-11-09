import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    redirect: "/item-list"
  },
  {
    path: "/item-show/:id",
    props: true,
    name: "item-show",
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/ItemShow.vue")
  },
  {
    path: "/item-list",
    name: "Item-list",
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/ItemList.vue")
  },
  {
    path: "/upload-camera",
    name: "Upload Camera",
    component: () => import("../views/UploadView.vue")
  },
  {
    path: "/upload-files",
    name: "Upload Files",
    component: () => import("../views/UploadFilesView.vue")
  },
  {
    path: "/trigger",
    name: "Trigger Capture",
    component: () => import("../views/TriggerView.vue")
  },
  {
    path: "/config",
    name: "Config",
    component: () => import("../views/Config.vue")
  },
  {
    path: "/about",
    name: "About",
    component: () => import("../views/About.vue")
  }
];

const router = new VueRouter({
  routes
});

export default router;
