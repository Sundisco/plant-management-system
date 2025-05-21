                        sx={{
                          position: 'relative',
                          height: 24,
                          bgcolor: count === 0 ? 'grey.100' : 'info.main',
                          borderRadius: 1.5,
                          cursor: 'pointer',
                          overflow: 'hidden',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            opacity: 0.9,
                            transform: 'scale(1.02)',
                          }
                        }} 