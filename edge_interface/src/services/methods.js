// import Api from "@/services/api";
import { baseURL } from "@/services/api";

function getUrlBinariesListByItem(item) {
  const sensorsDict = item.sensors;
  var urlBinariesList = [];
  for (var key in sensorsDict) {
    let value = sensorsDict[key];
    console.log(value);
    let urlBinary = getUrlBinary(item._id, value.binary_filename);
    urlBinariesList.push(urlBinary);
  }
  console.log(urlBinariesList);
  return urlBinariesList;
}

function getSensorsIdList(item) {
  if (item && item.sensors) return Object.keys(item.sensors);
  else return [];
}

function getSensorsInferences(item) {
  var sensorsInferences = [];
  for (var key in item.inferences) {
    sensorsInferences.push(item.inferences[key][0]);
  }
  return sensorsInferences;
}

function getUrlBinary(itemId, binaryName) {
  return `${baseURL}/items/${itemId}/binaries/${binaryName}`;
}

export {
  getSensorsIdList,
  getSensorsInferences,
  getUrlBinary,
  getUrlBinariesListByItem
};
