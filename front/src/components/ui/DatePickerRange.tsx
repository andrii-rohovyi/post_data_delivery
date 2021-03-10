import { DatePicker } from "antd";

const { RangePicker } = DatePicker;

export const DatePickerRange = ({ input, meta, ...rest }: any) => {
    return(
    <RangePicker
        {...input}
        {...rest}
        min={1}
        max={10}
        defaultValue={3}
        onChange={(value: any) => input.onChange(value)}
        errorText={meta.touched ? meta.error : ''}
    />
)}