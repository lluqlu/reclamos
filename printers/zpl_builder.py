import textwrap
from domain.models import Ticket, ProblemaTipo
from config import LABEL_WIDTH, LABEL_HEIGHT




LOGO_GFA = (
"^FO50,50^GFA,6426,6426,34,N03hOFC,L01hSF,L0hTFE,K03hUF8,K0hVFE,J03hWF8,J0hXFC,"
"I01hXFE,I03hYF8,I07hYFC,I0iFE,001KFChO07JFE,003JF8hQ03JF,007IFChS0JF8,00JFhT03IFC,"
"00IFEhT01IFE,01IFChU07FFE,03IF8hU03IF,03IFhV01IF,07FFEhW0IF8,07FFChW0IF8,0IF8hW07FFC,"
"0IFhX03FFC,0IFhX03FFE,1FFEL0hLFCK01FFE,1FFEK07hMF8J01FFE,3FFCJ01hNFEK0IF,3FFCJ07hOF8J0IF,"
"3FF8J0hPFCJ07FF,3FF8I01hPFEJ07FF,7FF8I03hPFEJ07FF8,7FFJ07hQFJ03FF8,7FFJ07hQF8I03FF8,"
"7FFJ0hRF8I03FF8,7FFJ0hRFCI03FF8,7FFI01IFChK0IFCI03FF8,7FFI01IFhL03FFCI01FFC,FFEI01FFEhL01FFCI01FFC,"
"FFEI01FFChL01FFCI01FFC,:FFEI01FFChM0FFEI01FFC,FFEI01FFChL01FFCI01FFC,:FFEI01FFEhL01FFCI01FFC,"
"FFEI01IFhL03FFCI01FFC,IFJ0JFhK0IFCI01FFC,7FFJ0WFEO07gJFCI03FF8,7FFJ0XFEN07gJF8I03FF8,7FFJ07XF8M07gJF8I03FF8,"
"7FFJ03XFEM07gJFJ03FF8,7FFJ03YF8L07gIFEJ03FF8,7FF8I01YFEL07gIFEJ07FF8,3FF8J0gFL07gIFCJ07FF,3FF8J03YF8K07gIF8J07FF,"
"3FFCJ01YFCK07gHFEK0IF,3FFCK03XFEK07gHF8K0IF,1FFCL03XFK07gGFCK01FFE,1FFEg07JF8J07FFgK01FFE,1FFEgG0JFCJ07FFgK03FFE,"
"0IFgG01IFEJ07FFgK03FFC,0IF8gG0IFEJ07FFgK07FFC,07FF8gG03IFJ07FFgK0IF8,07FFCgG01IF8I07FFgK0IF8,03FFEgH0IF8I07FFgJ01IF,"
"03IFgH07FFCI07FFgJ03IF,01IF8gG07FFCI07FFgJ07FFE,01IFCgG03FFEI07FFgI01IFE,00JFgG01FFEI07FFgI03IFC,007IFCg01IFI07FFgI0JF8,"
"003JFgG0IFI07FFgH07JF,003KFg07FFI07FFgG07JFE,001gFCJ07FF8007FFJ0gHFE,I0gGF8I07FF8007FFJ0gHFC,I07gFEI03FF8007FFJ0gHF,"
"I01gGFI03FFC007FFJ0gGFE,J0gGF8003FFC007FFJ0gGFC,J07gFC001FFC007FFJ0gGF,J01gFE001FFC007FFJ0gFE,"
"K07YFE001FFC007FFJ0gF8,K01gF001FFE007FFJ0YFC,L03YFI0FFE007FFJ0XFE,M01XF800FFE007FFJ0WFC,gI0IF800FFE007FFJ0FFE,"
"gI07FF800FFE007FFJ0FFE,gI03FF800FFE007FFJ0FFE,::::gI07FF800FFE007FFJ0FFE,gI0IF800FFE007FFJ0FFE,3gKF800FFE007FFJ0FFE,"
"3gKFI0FFE007FFJ0FFE,:3gJFE001FFE007FFJ0FFE,3gJFE001FFC007FFJ0FFE,3gJFC001FFC007FFJ0FFE,3gJF8001FFC007FFJ0FFE,"
"3gJFI03FFC007FFJ0FFE,3gIFEI03FF8007FFJ0FFE,3gIF8I03FF8007FFJ0FFE,3gHFCJ07FF8007FFJ0FFE,3FF8gJ07FF8007FFJ0FFE,"
"3FF8gJ0IFI07FFJ0FFE,:3FF8gI01IFI07FFJ0FFE,3FF8gI01FFEI07FFJ0FFE,3FF8gI03FFEI07FFJ0FFE,3FF8gI07FFCI07FFJ0FFE,"
"3FF8gI0IFCI07FFJ0FFE,3FF8gH01IF8I07FFJ0FFE,3FF8gH03IF8I07FFJ0FFE,3FF8gH07IFJ07FFJ0FFE,3FF8gG01IFEJ07FFJ0FFE,"
"3FF8gG03IFEJ07FFJ0FFE,3FF8g01JFCJ07FFJ0FFE,3FF8Y01KF8J07FFJ0FFE,^FS"
)




def zpl_escape(text: str) -> str:
    return text.replace('^', ' ').replace('~', ' ').replace('\\', '/')




def build_ticket_zpl(ticket: Ticket) -> str:
    # Texto
    titulo = f"Reclamo {ticket.id}"
    agente_line = f"Agente: {ticket.agente}"
    fechahora = f"Fecha: {ticket.ts.strftime('%d/%m/%Y')} Hora: {ticket.ts.strftime('%H:%M:%S')}"
    cliente_line = f"Cliente: {ticket.cliente_numero} - {ticket.cliente.nombre} {ticket.cliente.apellido}".strip()
    med_line = f"Medidor: {ticket.cliente.medidor}"
    tipo_line = (
        f"Motivo: {ticket.tipo.value} - {ticket.otro_detalle}" if (ticket.tipo == ProblemaTipo.OTRO and ticket.otro_detalle)
        else f"Motivo: {ticket.tipo.value}"
    )


    # Dirección y comentarios multilinea
    dir_lines = textwrap.wrap("Dom.: " + (ticket.cliente.direccion or ''), width=34)
    comment_lines = textwrap.wrap(ticket.comentarios or '', width=34)


    z = [
        '^XA',
        f'^PW{LABEL_WIDTH}',
        f'^LL{LABEL_HEIGHT}',
        '^LH0,0',
        '^CI28',
        LOGO_GFA,
        '^CF0,32',
        '^FO20,200^FD' + zpl_escape(titulo) + '^FS',
        '^FO430,190^BQN,2,4',
        '^FDLA,' + zpl_escape(ticket.id) + '^FS',
        '^FO20,240^GB536,2,2^FS',
        '^CF0,26',
        '^FO20,260^FD' + zpl_escape(agente_line) + '^FS',
        '^FO20,290^FD' + zpl_escape(fechahora) + '^FS',
        '^FO20,320^FD' + zpl_escape(cliente_line) + '^FS',
    ]


    y = 350
    for line in dir_lines:
        z.append(f'^FO20,{y}^FD' + zpl_escape(line) + '^FS')
        y += 28


    z += [
        f'^FO20,{y}^FD' + zpl_escape(med_line) + '^FS',
        f'^FO20,{y+30}^FD' + zpl_escape(tipo_line) + '^FS',
        f'^FO20,{y+60}^GB536,2,2^FS',
        '^CF0,24',
        f'^FO20,{y+80}^FD' + zpl_escape('Informe y observaciones:') + '^FS',
    ]


    y_comments = y + 110
    for line in comment_lines[:9]:
        z.append(f'^FO20,{y_comments}^FD' + zpl_escape(line) + '^FS')
        y_comments += 28


    footer_y = max(y_comments + 20, 760)
    z += [
        f'^FO20,{footer_y}^GB536,2,2^FS',
        '^CF0,26',
        f'^FO20,{footer_y+20}^FD' + zpl_escape('N° de reclamo: ' + ticket.id) + '^FS',
        '^XZ'
    ]


    return "\n".join(z)