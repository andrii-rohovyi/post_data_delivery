import { InputNumber } from "antd";

export const InputNumberComponent = ({ input, meta, ...rest }: any) => {
    console.log(rest, input);
    return(
    <InputNumber
        {...input}
        {...rest}
        min={1}
        max={10}
        defaultValue={3}
        onChange={(value: any) => input.onChange(value)}
        errorText={meta.touched ? meta.error : ''}
    />
)}