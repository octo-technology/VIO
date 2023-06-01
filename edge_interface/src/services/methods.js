// import Api from "@/services/api";
import { baseURL } from '@/services/api.js'

function getUrlBinary(itemId, binaryName) {
  return `${baseURL}/items/${itemId}/binaries/${binaryName}`
}

function getUrlBinariesListByItem(item) {
  const sensorsDict = item.sensors
  const urlBinariesList = []
  for (const key in sensorsDict) { // eslint-disable-line
    const value = sensorsDict[key]
    const urlBinary = getUrlBinary(item.id, value.binary_filename)
    urlBinariesList.push(urlBinary)
  }
  return urlBinariesList
}

function getSensorsIdList(item) {
  if (item && item.sensors) return Object.keys(item.sensors)
  return []
}

export { getSensorsIdList, getUrlBinary, getUrlBinariesListByItem }
