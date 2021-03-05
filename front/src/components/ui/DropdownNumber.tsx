import { Menu, Dropdown, Button } from 'antd';

import { DownOutlined } from '@ant-design/icons';

export const DropdownNumber = ({ input, meta, ...rest }: any) => {

const menu = (
  <Menu onClick={(e) => {
      input.onChange(e.key);
  }
  }>
    <Menu.Item key={100}>
      100 kg
    </Menu.Item>
    <Menu.Item key={200} >
      200 kg
    </Menu.Item>
    <Menu.Item key={500} >
      500 kg
    </Menu.Item>
    <Menu.Item key={1000} >
      1000 kg
    </Menu.Item>
    <Menu.Item key={1500} >
      1500 kg
    </Menu.Item>
    <Menu.Item key={3000}>
      3000 kg
    </Menu.Item>
  </Menu>
);
    return(
        <Dropdown
            {...input}
            {...rest}
            overlay={menu}>
            {/*onChange={(value: any) => input.onChange(value)}*/}
      <Button
          style={{marginLeft: "30px"}}
      >
          {input.value ? input.value : " 100 "}<DownOutlined />
      </Button>
    </Dropdown>
)}