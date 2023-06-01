// import Api from "@/services/api";
import { baseURL } from '@/services/api'

function getUrlBinariesListByItem(item) {
  const sensorsDict = item.sensors
  const urlBinariesList = []
  for (const key in sensorsDict) {
    const value = sensorsDict[key]
    console.log(value)
    const urlBinary = getUrlBinary(item.id, value.binary_filename)
    urlBinariesList.push(urlBinary)
  }
  console.log(urlBinariesList)
  return urlBinariesList
}

function getSensorsIdList(item) {
  if (item && item.sensors) return Object.keys(item.sensors)
  return []
}

function getSensorsInferences(item) {
  const sensorsInferences = []
  for (const key in item.inferences) {
    sensorsInferences.push(item.inferences[key][0])
  }
  return sensorsInferences
}

function getUrlBinary(itemId, binaryName) {
  return `${baseURL}/items/${itemId}/binaries/${binaryName}`
}

export { getSensorsIdList, getSensorsInferences, getUrlBinary, getUrlBinariesListByItem }
