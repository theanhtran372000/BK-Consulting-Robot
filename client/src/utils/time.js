import dayjs from "dayjs";

export const delay = ms => new Promise(res => setTimeout(res, ms));

export const getNow = () => new Date()

export const getStartOfToday = () => {
    const now = new Date()
    now.setHours(0, 0, 0, 0)
    return now
}

export const getEndOfToday = () => {
    const now = new Date()
    now.setHours(23,59,59,999)
    return now
}

export const fromDateToDayJS = (date) => dayjs(date)
export const fromDayJSToEpochSecTime = (dayjsObject) => dayjsObject.unix()
export const fromDayJSToEpochMiliSecTime = (dayjsObject) => dayjsObject.valueOf()
export const fromDayJSToDate = (dayjsObject) => dayjsObject.toDate()
export const fromUnixTimeToDateString = (epoch) => {
    const d = new Date(0)
    d.setUTCSeconds(epoch)
    return d.toString()
}
export const fromUnixTimeToDate = (epoch) => {
    const d = new Date(0)
    d.setUTCSeconds(epoch)
    return d
}