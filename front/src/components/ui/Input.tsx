import { Input } from 'antd';
import Icon from "@ant-design/icons";

const kek = <Icon type="smile" style={{fontSize: "50px"}}/>;

export const InputComponent = ({ input, meta, ...rest }: any) => (
    <Input
        {...input}
        {...rest}
        onChange={(value: any) => input.onChange(value)}
        size="large"
        suffix={kek}
    />
)