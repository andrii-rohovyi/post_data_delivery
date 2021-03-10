import {TimePicker} from "antd";

const { RangePicker } = TimePicker;


export const RangeTimePicker = ({ input, meta, ...rest }: any) => {
    return(
    <RangePicker
        {...input}
        {...rest}
        style={{width: "37%"}}
        format="HH:mm"
        onChange={(value: any) => input.onChange(value)}
        errorText={meta.touched ? meta.error : ''}
    />
)}