import {Select} from "antd";

const { Option } = Select;

export const SelectComponent = ({ input, meta, options, ...rest }: any) => (
    <Select
        {...input}
        {...rest}
        onChange={(value: any) => input.onChange(value)}
        defaultValue={options[0]}
    >
        {options.map((option: any) => (
            <>
            <Option value={option}>{option}</Option>
            </>
        ))}

      </Select>
)