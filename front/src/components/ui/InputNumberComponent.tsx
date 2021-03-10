import { InputNumber } from "antd";

export const InputNumberComponent = ({ input, meta, ...rest }: any) => {
    return(
    <InputNumber
        {...input}
        {...rest}
        min={1}
        max={1000}
        defaultValue={3}
        onChange={(value: any) => input.onChange(value)}
        errorText={meta.touched ? meta.error : ''}
    />
)}