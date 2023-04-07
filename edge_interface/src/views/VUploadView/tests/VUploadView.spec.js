import { shallowMount } from '@vue/test-utils'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from "vuetify";
import VUploadView from '../VUploadView.vue'

Vue.use(Vuex)
Vue.use(Vuetify);

let wrapper
describe('VUploadView.vue', () => {
  beforeEach(() => {
    wrapper = shallowMount(VUploadView, {
      mocks: {
      $store: new Vuex.Store({
        getters: {
          imagePath: () => null,
        }
      }),
      }
    })
  })
  it('should mount the component', () => {
    expect(wrapper).toBeDefined()
  })
  it('should check the name of my vue', () => {
    expect(wrapper.name()).toEqual('VUploadView')
  })
  describe('#methods', () => {
    it('#getCameraDevices', () => {
      // GIVEN
      const devicesUpdate = ["device1"]

      // WHEN
      wrapper.vm.getCameraDevices(devicesUpdate)

      // THEN
      expect(wrapper.vm.devices).toEqual(devicesUpdate)
    })
    it('#onCameraDeviceChange', () => {
      // GIVEN
      const deviceIdUpdate = "device1"

      // WHEN
      wrapper.vm.onCameraDeviceChange(deviceIdUpdate)

      // THEN
      expect(wrapper.vm.deviceId).toEqual(deviceIdUpdate)
    })
    describe('#onCaptureImage', () => {
      it('should update imagePath in store when imagePath is null', () => {
        // GIVEN
        let setImagePathStub = jest.fn()
        wrapper = shallowMount(VUploadView, {
          mocks: {
          $store: new Vuex.Store({
            getters: {
              imagePath: () => null,
            },
            mutations: {
              'SET_IMAGE_PATH': setImagePathStub
            }
          }),
          },
          methods: { captureImage: () => 'an_image' }
        })

        // WHEN
        wrapper.vm.onCaptureImage()

        // THEN
        expect(setImagePathStub.mock.calls.length).toBe(1)
        expect(setImagePathStub.mock.calls[0]).toEqual([{}, 'an_image'])
      })
      it('should reset imagePath to null in store when imagePath is not null', () => {
        // GIVEN
        let setImagePathStub = jest.fn()
        wrapper = shallowMount(VUploadView, {
          mocks: {
          $store: new Vuex.Store({
            getters: {
              imagePath: () => 'an_image_there',
            },
            mutations: {
              'SET_IMAGE_PATH': setImagePathStub
            }
          }),
          },
          methods: { captureImage: () => 'an_image' }
        })

        // WHEN
        wrapper.vm.onCaptureImage()

        // THEN
        expect(setImagePathStub.mock.calls.length).toBe(1)
        expect(setImagePathStub.mock.calls[0]).toEqual([{}, null])
      })
    })
  })
  describe("#computed", () => {
    it('#device', () => {
      // GIVEN
      let devices = [{ deviceId: "bapo"}, { devideId: "totocto" }]
      let deviceId = "bapo"
      wrapper.setData({ devices: devices, deviceId: deviceId })
      let expectedDevice = { deviceId: "bapo" }

      // THEN
      expect(wrapper.vm.device).toEqual(expectedDevice)
    })
    describe('#isAnyImageCaptured', () => {
      it('#isAnyImageCaptured should return False when imagePath is null', () => {
        expect(wrapper.vm.isAnyImageCaptured).toBeFalse()
      })
      it('#isAnyImageCaptured should return True when imagePath is not null', () => {
        wrapper = shallowMount(VUploadView, {
          mocks: {
          $store: new Vuex.Store({
            getters: {
              imagePath: () => 'an_image',
            }
          })
        }})
        expect(wrapper.vm.isAnyImageCaptured).toBeTrue()
      })
    })
  })
})
