// src/components/Message.js
import React from 'react';
import { ListItem, ListItemText } from '@mui/material';

const Message = ({ message }) => {
  const alignment = message.origen === 'usuario' ? 'right' : 'left';

  return (
    <ListItem sx={{ justifyContent: alignment === 'right' ? 'flex-end' : 'flex-start' }}>
      <ListItemText
        primary={message.origen === 'usuario' ? 'Tú' : 'ChatBot'}
        secondary={message.texto}
        sx={{ textAlign: alignment }}
      />
    </ListItem>
  );
};

export default Message;
