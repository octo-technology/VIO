import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    redirect: () => ('/camera')
  },
  {
    path: "/camera",
    name: "Simple-Camera",
    component: () => import("../views/SimpleCameraView.vue")
  },
  {
    path: "/result/:itemId",
    name: "Simple-Result",
    component: () => import("../views/SimpleResultView.vue")
  },
  {
    path: "/home",
    name: "Home-Camera",
    component: () => import("../views/UploadView.vue")
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
    path: "/item-gallery",
    name: "Item-gallery",
    component: () =>
      import(/* webpackChunkName: "about" */ "../views/ItemGallery.vue")
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
    path: "/shopfloor",
    name: "Shopfloor UI",
    component: () => import("../views/Shopfloor.vue")
  },
  {
    path: "/config",
    name: "Config",
    component: () => import("../views/Config2.vue")
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
