import xml.etree.ElementTree as etree

#from lxml import etree #in caso di uso di lxml, utile per gli XSD

class ControlliFatturaElettronica(Object):
    pass

def lencheck(item,**kargs):

    if kargs[type] == "string":
        if kargs[min] and kargs[max]:
            return len(item) < kargs[max] and len(item) > kargs[min]
        elif kargs[max]:
            return len(item) < kargs[max]
        elif min:
            return len(item) > kargs[min]

def piva(value): 
    
    if (len(value) != 11) or not value.isdigit(): 
        return False 
    value = map(int, value)
    checksum = sum(map(lambda x: value[x], xrange(0, 10, 2)))
    checksum += sum(map(lambda x: [value[x]*2,(2*value[x])-9][(2*value[x]) > 9], xrange(1, 10, 2)))
    checksum = 10 - (checksum % 10) 
    return value[10] == checksum
            

class FatturaElettronica:

    def __init__(self,FatturaElettronicaHeader, FatturaElettronicaBody):
        self.FatturaElettronicaHeader = FatturaElettronicaHeader
        self.FatturaElettronicaBody = FatturaElettronicaBody

    def SerializeXML(self):
        FatturaElettronica = etree.Element("FatturaElettronica")
        FatturaElettronica.append(self.FatturaElettronicaHeader.SerializeXML())
        FatturaElettronica.append(self.FatturaElettronicaBody.SerializeXML())    
        return FatturaElettronica


class FatturaElettronicaHeader:
    
    def __init__(self,DatiTrasmissione, CedentePrestatore, CessionarioCommittente):
        self.DatiTrasmissione = DatiTrasmissione
        self.CedentePrestatore = CedentePrestatore
        self.CessionarioCommittente = CessionarioCommittente

    def SerializeXML(self):
        FatturaElettronicaHeader = etree.Element("FatturaElettronicaHeader")
        
        FatturaElettronicaHeader.append(self.DatiTrasmissione.SerializeXML())
        FatturaElettronicaHeader.append(self.CedentePrestatore.SerializeXML())
        
        # Optional Field
        try:
            FatturaElettronicaHeader.append(self.RappresentanteFiscale.SerializeXML())
            FatturaElettronicaHeader.append(self.TerzoIntermediarioOSoggettoEmittente.SerializeXML())
        except AttributeError:
            pass
        
        FatturaElettronicaHeader.append(self.CessionarioCommittente.SerializeXML())
        
        #Controllare e sistemare va anche controllato che il valore sia CC o TZ unici ammessi
        if self.SoggettoEmittente not None:
            SoggettoEmittente = etree.SubElement(FatturaElettronicaHeader,"SoggettoEmittente")
            SoggettoEmittente.text = self.SoggettoEmittente
            
        return FatturaElettronicaHeader


class DatiTrasmissione:

    def __init__(self,IdTrasmittente, ProgressivoInvio, FormatoTrasmissione = "SDI10", CodiceDestinatario):
        # warning: il nome file prevede 5 caratteri ma va concatenato il campo sottostante
        if len(self.ProgressivoInvio) > 10: raise ValueError("ProgressivoInvio Must be a string whit len >0 and <10")
        if len(self.CodiceDestinatario) > 6: raise ValueError("CodiceDestinatario Must be a string whit len >0 and <6")
        self.IdTrasmittente = IdTrasmittente
        self.ProgressivoInvio = ProgressivoInvio
        self.FormatoTrasmissione = FormatoTrasmissione
        self.CodiceDestinatario = CodiceDestinatario

    def SerializeXML(self):
        DatiTrasmissione = etree.Element("DatiTrasmissione")
        
        DatiTrasmissione.append(self.IdTrasmittente.SerializeXML())
        (etree.SubElement(DatiTrasmissione,"ProgressivoInvio")).text = self.ProgressivoInvio
        (etree.SubElement(DatiTrasmissione,"FormatoTrasmissione")).text = self.FormatoTrasmissione
        (etree.SubElement(DatiTrasmissione,"CodiceDestinatario")).text = self.CodiceDestinatario
        
        # Optional Field
        try:
            DatiTrasmissione.append(self.ContattiTrasmittente.SerializeXML())
        except AttributeError:
            pass
            
        return DatiTrasmissione


class IdTrasmittente:
    
    def __init__(self,IdPaese, IdCodice):
        # warning: il nome file prevede 5 caratteri ma va concatenato il campo sottostante
        if len(self.IdPaese) > 2: raise ValueError("IdPaese Must be a string whit len >0 and <=2 ES: IT,EU,ES")
        if len(self.IdCodice) > 6: raise ValueError("IdCodice Must be a string whit len >0 and <28")
        if IdPaese.lower() == 'it':
            if not piva(IdCodice) : raise ValueError("IdCodice for contry IT not valid")
        self.IdPaese = IdPaese
        self.IdCodice = IdCodice
    
    def SerializeXML(self):
        IdTrasmittente = etree.Element("IdTrasmittente")
        
        etree.SubElement(IdTrasmittente,"IdPaese").text = self.IdPaese
        etree.SubElement(IdTrasmittente,"IdCodice").text = self.IdCodice
            
        return IdTrasmittente

class ContattiTrasmittente:

    def __init__(self,Telefono, Email):
        # warning: caso uno dei due assenti non previsto, fix prossima release, nessun controlla sulla mail
        if len(self.Telefono) < 2 or len(self.Telefono) > 12 : raise ValueError("Telefono Must be a string whit len > 5 and <=12")
        if len(self.Email) < 7 or len(self.Email) > 256 : raise ValueError("Email Must be a string whit len >7 and <256")
        self.Telefono = Telefono
        self.Email = Email
    
    def SerializeXML(self):
        ContattiTrasmittente = etree.Element("ContattiTrasmittente")
        
        etree.SubElement(ContattiTrasmittente,"Telefono").text = self.Telefono
        etree.SubElement(ContattiTrasmittente,"Email").text = self.Email
            
        return ContattiTrasmittente

class CedentePrestatore:

    # RiferimentoAmministrazione non controllato 
    
    def __init__(self,DatiAnagrafici, Sede):
        self.DatiAnagrafici = DatiAnagrafici
        self.Sede = Sede

    def SerializeXML(self):
        CedentePrestatore = etree.Element("CedentePrestatore")
        
        CedentePrestatore.append(self.DatiAnagrafici.SerializeXML())
        CedentePrestatore.append(self.Sede.SerializeXML())
        
        # Optional Field
        try:
            CedentePrestatore.append(self.StabileOrganizzazione.SerializeXML())
        except AttributeError:
            pass
        # Optional Field
        try:
            CedentePrestatore.append(self.IscrizioneREA.SerializeXML())
        except AttributeError:
            pass
        # Optional Field
        try:
            CedentePrestatore.append(self.Contatti.SerializeXML())
        except AttributeError:
            pass
        try:
            etree.SubElement(CedentePrestatore,"RiferimentoAmministrazione").text = self.RiferimentoAmministrazione
        except AttributeError:
            pass
                        
        return CedentePrestatore

class DatiAnagrafici:
    IdFiscaleIVA # Stesso di IdTrasmittente eventualmente Raggrupparlo / estenderlo solo per il nome
    CodiceFiscale # numero di codice fiscale del cedente/prestatore. formato alfanumerico; lunghezza compresa tra  11 e 16 caratter*/
    Anagrafica
    AlboProfessionale # nome dell'albo professionale cui appartiene il  cedente/prestatore. formato alfanumerico; lunghezza massima  di 60 caratteri.*/
    ProvinciaAlbo #provincia dell'albo professionale.  formato alfanumerico; lunghezza di 2 caratteri.  */
    NumeroIscrizioneAlbo # numero di iscrizione all'albo professionale. formato alfanumerico; lunghezza  massima di 60 caratter*/
    DataIscrizioneAlbo #data di iscrizione all'albo professionale (espressa secondo  il formato ISO 8601:2004). formato alfanumerico; lunghezza  massima di 60 caratter*/
    RegimeFiscale # Dati Fissati da sistemare

class IdFiscaleIVA:
    IdPaese #IdPaese: codice del paese assegnante l’identifcativo fiscale al soggetto  trasmittente (secondo lo standard ISO 3166-1 alpha-2 code). 
    IdCodice # numero di identificazione fiscale del trasmittente (per i soggetti  stabiliti nel territorio dello Stato Italiano corrisponde al Codice Fiscale; per i non  residenti si fa riferimento all’identificativo fiscale assegnato dall’autorità del  paese di residenza). formato alfanumerico; lunghezza massima di 28 caratteri.

class Anagrafica:
    Denominazione # ditta, denominazione o ragione sociale del cedente/prestatore  del bene/servizio da valorizzare nei casi di persona non fisica; la valorizzazione  di questo campo è in alternativa a quella dei campi Nome e Cognome seguenti. formato alfanumerico; lunghezza massima di 80 caratteri.  Da valorizzare in alternativa ai campi Nome e Cognome seguenti.*/
    Nome  # Nome del cedente/prestatore del bene/servizio da valorizzare nei casi di  persona fisica; la valorizzazione di questo campo presuppone anche la  valorizzazione del campo Cognome ed è in alternativa a quella del campo  Denominazione. formato alfanumerico; lunghezza massima di 60 caratteri. Da  valorizzare insieme al campo Cognome ed in alternativa al campo  Denominazione.*/
    Cognome # Cognome: cognome del cedente/prestatore del bene/servizio da valorizzare nei  casi di persona fisica; la valorizzazione di questo campo presuppone anche la  valorizzazione del campo Nome ed è in alternativa a quella del campo  Denominazione.  formato alfanumerico; lunghezza massima di 60 caratteri. Da  valorizzare insieme al campo Nome ed in alternativa al campo  Denominazione.*/
    Titolo # titolo onorifico del cedente/prestatore. formato alfanumerico; lunghezza che va da 2 a 10 caratteri.  */
    CodEORI # numero del Codice EORI (Economic Operator Registration and  Identification) in base al Regolamento (CE) n. 312 del 16 aprile 2009. In vigore  dal 1 Luglio 2009 tale codice identifica gli operatori economici nei rapporti con le  autorità doganali sull'intero territorio dell'Unione Europea. formato alfanumerico; lunghezza che va da 13 a 17 caratteri*/

class Sede:
    Indirizzo #indirizzo del cedente/prestatore del bene/servizio; deve essere  valorizzato con il nome della via, piazza, etc., comprensivo, se si vuole, del  numero civico formato alfanumerico; lunghezza  massima di 60 caratter*/
    NumeroCivico #numero civico relativo all’indirizzo specificato nel campo  precedente; si può omettere se già riportato nel campo precedente.  formato alfanumerico; lunghezza massima di  8 caratteri.*/
    CAP # Codice di Avviamento Postale relativo all’indirizzo. formato numerico; lunghezza di 5 caratteri.  */
    Comune # Comune cui si riferisce l'indirizzo formato alfanumerico; lunghezza massima di 60  caratteri.*/
    Provincia # sigla della provincia di appartenenza del comune. formato alfanumerico; lunghezza di 2 caratteri.  */
    Nazione # codice della nazione espresso secondo lo standard ISO 3166-1  alpha-2 code sigla della nazione espressa secondo lo standard  ISO 3166-1 alpha-2 code. 

class StabileOrganizzazione:
    Indirizzo # indirizzo del cedente/prestatore del bene/servizio; deve essere valorizzato con il nome della via, piazza, etc., comprensivo, se si vuole, del numero civico*/
    NumeroCivico # numero civico relativo all’indirizzo specificato nel campo precedente; si può omettere se già riportato nel campo precedente.*/
    CAP # Codice di Avviamento Postale relativo all’indirizzo.*/
    Comune # Comune cui si riferisce l’indirizzo.*/
    Provincia # /*sigla della provincia di appartenenza del comune.*/
    Nazione # codice della nazione espresso secondo lo standard ISO 3166-1 alpha-2 code*/

class IscrizioneREA:
    Ufficio # sigla della provincia ove ha sede l'Ufficio del Registro delle Imprese presso il quale è registrata la società. formato alfanumerico; lunghezza di 2 caratteri.*/
    NumeroREA # /*numero di repertorio con il quale la società è iscritta nel Registro delle Imprese. formato alfanumerico; lunghezza massima di 20 caratteri.*/
    CapitaleSociale # indica il capitale sociale quale somma effettivamente versata e quale risulta esistente dall’utlimo bilancio della società; questo campo è valorizzato nei soli casi di società di capitali (SpA, SApA, SRL). formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    SocioUnic # questo campo è valorizzato nei casi di società per azioni e a responsabilità limitata; indica se queste si compongono di un unico socio o di più soci. formato alfanumerico; lunghezza di 2 caratteri; i valori ammessi sono i seguenti: SU la società è a socio unico. SM la società NON è a socio unico.
    StatoLiquidazione # indica se la società si trova in stato di liquidazione oppure no formato alfanumerico; lunghezza di 2 caratteri; i valori ammessi sono i seguenti: LS la società è in stato di liquidazione. LN la società NON è in stato di liquidazione.

class Contatti
    Telefono # contatto telefonico fisso / mobile del cedente/prestatore. formato alfanumerico; lunghezza che va da 5 a 12 caratteri.*/
    Fax #numero di fax del cedente/prestatore.formato alfanumerico; lunghezza che va da 5 a 12 caratteri.*/
    Email # indirizzo di posta elettronica del cedente/prestatore. formato alfanumerico; lunghezza che va da 7 a 256 caratteri.*/

class RappresentanteFiscale:
    DatiAnagrafici

class CessionarioCommittente:
    DatiAnagrafici
    Sede

class TerzoIntermediarioOSoggettoEmittente
    DatiAnagrafici

class FatturaElettronicaBody:
    DatiGenerali
    DatiBeniServizi
    DatiVeicoli # Presenti nei casi di cessioni tra paesi membri di mezzi di trasporto nuovi. Dati  relativi ai veicoli di cui all’art. 38, comma 4 del DL 331 del 1993.
    DatiPagamento
    Allegati

class DatiGenerali:
    DatiGeneraliDocumento
    DatiOrdineAcquisto # [Lista Multipla] /*Dati relativi all’ordine di acquisto dal quale scaturisce la cessione/prestazione  oggetto del documento fattura. DatiOrdineAcquisto, DatiContratto, DatiConvenzione, DatiRicezione e  DatiFattureCollegateI 5 elementi in questione utilizzano tutti il tipo DatiDocumentiCorrelatiType, di  seguito descritto. */
    DatiContratto # [Lista Multipla] Dati relativi al contratto dal quale scaturisce la cessione/prestazione oggetto del documento fattura.*/
    DatiConvenzione # [Lista Multipla]
    DatiRicezione # [Lista Multipla] Dati relativi alla ricezione dei beni/servizi oggetto del documento fattura.*/
    DatiFattureCollegate # [Lista Multipla] Dati relativi alla fattura alla quale si collega il documento in oggetto.*/
    DatiSAL
    DatiDDT
    DatiTrasporto
    NormaDiRiferimento # norma di riferimento, comunitaria o nazionale, da indicare nei casi in cui il cessionario/committente è debitore di imposta in luogo del cedente/prestatore (reverse charge), o nei casi in cui sia tenuto ad emettere autofattura. formato alfanumerico; lunghezza massima di 100 caratteri.*/
    FatturaPrincipale # Presente nei casi di fatture per operazioni accessorie, emesse dagli  ‘autotrasportatori’ per usufruire delle agevolazioni in materia di registrazione e  pagamento IVA. */

class DatiGeneraliDocumento:
    TipoDocumento # tipologia del documento oggetto della trasmissione (fattura,  acconto/anticipo su fattura, nota di credito, parcella …). formato alfanumerico; lunghezza di 4  caratteri; i valori ammessi sono i seguenti:  

    """ TD01 Fattura
        TD02 Acconto/Anticipo su fattura
        TD03 Acconto/Anticipo su parcella
        TD04 Nota di Credito
        TD05 Nota di Debito
        TD06 Parcella
    """
    Divisa # Divisa: tipo di valuta utilizzata per l'indicazione degli importi espressa secondo  lo standard ISO 4217 alpha-3:2001.   questo campo deve essere espresso secondo lo  standard ISO 4217 alpha-3:2001 (es.: EUR, USD, GBP, CZK………).  */
    Data # data del documento (espressa secondo il formato ISO 8601:2004). la data deve essere rappresentata secondo il formato  ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.  */
    Numero #numero progressivo attribuito dal cedente/prestatore al documento. formato alfanumerico; lunghezza massima di 20  caratteri.  */
    DatiRitenuta # Nei casi in cui sia applicabile la ritenuta, vanno valorizzati i seguenti campi:  */
    DatiBollo # Nei casi in cui sia prevista l’imposta di bollo, vanno valorizzati i seguenti campi:*/
    DatiCassaPrevidenziale # Nei casi in cui sia previsto il contributo cassa previdenziale, vanno valorizzati i  seguenti campi:  */
    ScontoMaggiorazione
    ImportoTotaleDocumento # importo totale del documento comprensivo di imposta a debito del cessionario/committente. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    Arrotondamento # importo dell’arrotondamento sul totale documento, qualora presente. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    Causale # descrizione della causale del documento. formato alfanumerico; lunghezza massima di 200 caratteri.*/ 
    Art73 # indica se il documento è stato emesso secondo modalità e termini stabiliti con decreto ministeriale ai sensi dell'articolo 73 del DPR 633/72 (ciò consente al cedente/prestatore l'emissione nello stesso anno di più documenti aventi stesso numero). formato alfanumerico; lunghezza di 2 caratteri; il valore ammesso è: SI documento emesso secondo modalità e termini stabiliti con DM ai sensi del’’art. 73 del DPR 633/72.*/

class DatiOrdineAcquisto:
    RiferimentoNumeroLinea #numero della linea o delle linee di dettaglio della fattura alle quali si riferisce l’ordine di acquisto così come identificato dai tre campi successivi (IdDocumento, Data, NumItem); nel caso in cui l’ordine di acquisto si riferisce all’intera fattura, questo campo non deve essere valorizzato. formato numerico;*/
    IdDocumento #numero dell’ ordine di acquisto associato alla fattura o alla  linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza*/
    Data # data dell’ ordine di acquisto associato alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea (espressa secondo il formato ISO 8601:2004). La data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    NumItem # identificativo della singola voce (linea di ordine) all'interno dell’ordine di acquisto associata alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza massima di 20 caratter*/
    CodiceCommessaConvenzione # codice della commessa o della convenzione collegata alla fattura formato alfanumerico; lunghezza massima di 100 caratteri*/
    CodiceCUP # codice gestito dal CIPE che caratterizza ogni progetto di investimento pubblico (Codice Unitario Progetto). formato alfanumerico; lunghezza massima di 15 caratteri.*/
    CodiceCIG #Codice Identificativo della Gara formato alfanumerico; lunghezza massima di 15 caratteri.*/

class DatiContratto:
    RiferimentoNumeroLinea #numero della linea o delle linee di dettaglio della fattura alle quali si riferisce l’ordine di acquisto così come identificato dai tre campi successivi (IdDocumento, Data, NumItem); nel caso in cui l’ordine di acquisto si riferisce all’intera fattura, questo campo non deve essere valorizzato. formato numerico;*/
    IdDocumento #numero dell’ ordine di acquisto associato alla fattura o alla  linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza*/
    Data #data dell’ ordine di acquisto associato alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea (espressa secondo il formato ISO 8601:2004). a data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    NumItem # identificativo della singola voce (linea di ordine) all'interno dell’ordine di acquisto associata alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza massima di 20 caratter*/
    CodiceCommessaConvenzione # codice della commessa o della convenzione collegata alla fattura formato alfanumerico; lunghezza massima di 100 caratteri*/
    CodiceCUP # codice gestito dal CIPE che caratterizza ogni progetto di investimento pubblico (Codice Unitario Progetto). formato alfanumerico; lunghezza massima di 15 caratteri.*/
    CodiceCIG # Codice Identificativo della Gara formato alfanumerico; lunghezza massima di 15 caratteri.*/

class DatiConvenzione:
    RiferimentoNumeroLinea #numero della linea o delle linee di dettaglio della fattura alle quali si riferisce l’ordine di acquisto così come identificato dai tre campi successivi (IdDocumento, Data, NumItem); nel caso in cui l’ordine di acquisto si riferisce all’intera fattura, questo campo non deve essere valorizzato. formato numerico;*/
    IdDocumento # numero dell’ ordine di acquisto associato alla fattura o alla  linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza*/
    Data # data dell’ ordine di acquisto associato alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea (espressa secondo il formato ISO 8601:2004). La data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    NumItem # identificativo della singola voce (linea di ordine) all'interno dell’ordine di acquisto associata alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza massima di 20 caratter*/
    CodiceCommessaConvenzione # codice della commessa o della convenzione collegata alla fattura formato alfanumerico; lunghezza massima di 100 caratteri*/
    CodiceCUP # codice gestito dal CIPE che caratterizza ogni progetto di investimento pubblico (Codice Unitario Progetto). formato alfanumerico; lunghezza massima di 15 caratteri.*/
    CodiceCIG #Codice Identificativo della Gara. formato alfanumerico; lunghezza massima di 15 caratteri.*/

class DatiRicezione:
    RiferimentoNumeroLinea #numero della linea o delle linee di dettaglio della fattura alle quali si riferisce l’ordine di acquisto così come identificato dai tre campi successivi (IdDocumento, Data, NumItem); nel caso in cui l’ordine di acquisto si riferisce all’intera fattura, questo campo non deve essere valorizzato. formato numerico;*/
    IdDocumento #numero dell’ ordine di acquisto associato alla fattura o alla  linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza*/
    Data # data dell’ ordine di acquisto associato alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea (espressa secondo il formato ISO 8601:2004). a data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    NumItem #identificativo della singola voce (linea di ordine) all'interno dell’ordine di acquisto associata alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza massima di 20 caratter*/
    CodiceCommessaConvenzione #codice della commessa o della convenzione collegata alla fattura formato alfanumerico; lunghezza massima di 100 caratteri*/
    CodiceCUP #codice gestito dal CIPE che caratterizza ogni progetto di investimento pubblico (Codice Unitario Progetto). formato alfanumerico; lunghezza massima di 15 caratteri.*/
    CodiceCIG #Codice Identificativo della Gara formato alfanumerico; lunghezza massima di 15 caratteri.*/
    
class DatiFattureCollegate
    RiferimentoNumeroLinea; /*numero della linea o delle linee di dettaglio della fattura alle quali si riferisce l’ordine di acquisto così come identificato dai tre campi successivi (IdDocumento, Data, NumItem); nel caso in cui l’ordine di acquisto si riferisce all’intera fattura, questo campo non deve essere valorizzato. formato numerico;*/
    IdDocumento #numero dell’ ordine di acquisto associato alla fattura o alla  linea/linee di fattura indicate nel campo RiferimentoNumeroLinea.  formato alfanumerico; lunghezza*/
    Data # data dell’ ordine di acquisto associato alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea (espressa secondo il formato ISO 8601:2004). La data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    NumItem # identificativo della singola voce (linea di ordine) all'interno dell’ordine di acquisto associata alla fattura o alla linea/linee di fattura indicate nel campo RiferimentoNumeroLinea. formato alfanumerico; lunghezza massima di 20 caratter*/
    CodiceCommessaConvenzione # codice della commessa o della convenzione collegata alla fattura formato alfanumerico; lunghezza massima di 100 caratteri*/
    CodiceCUP # codice gestito dal CIPE che caratterizza ogni progetto di investimento pubblico (Codice Unitario Progetto). formato alfanumerico; lunghezza massima di 15 caratteri.*/
    CodiceCIG # Codice Identificativo della Gara formato alfanumerico; lunghezza massima di 15 caratteri.*/

class DatiSAL
    RiferimentoFase; /*fase dello stato avanzamento cui la fattura si riferisce. formato numerico; lunghezza massima di 3 caratteri.*/

class DatiDDT
    NumeroDDT #numero del Documento Di Trasporto formato alfanumerico; lunghezza massima di 20 caratteri.*/
    DataDDT #data del Documento Di Trasporto (espressa secondo il formato ISO 8601:2004). la data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    RiferimentoNumeroLinea #numero della linea o delle linee di dettaglio della fattura alle quali si riferisce il DDT (così come identificato dai campi NumeroDDT e DataDDT); nel caso in cui il documento di trasporto si riferisce all’intera fattura, questo campo non deve essere valorizzato. formato numerico; lunghezza massima di 4 caratteri.*/

class DatiTrasporto:
    DatiAnagraficiVettore # Stessi campi di DatiAnagrafici*/
    CausaleTrasporto # causale del trasporto.formato alfanumerico; lunghezza massima di 100 caratteri.*/
    NumeroColli # numero dei colli trasportati. formato numerico; lunghezza massima di 4 caratteri.*/
    Descrizione # descrizione (natura, qualità, aspetto …) relativa ai colli trasportati. formato alfanumerico; lunghezza massima di 100 caratteri.*/
    UnitaMisuraPeso # unità di misura riferita al peso della merce trasportata. formato alfanumerico; lunghezza massima di 10 caratteri.*/
    PesoLordo # peso lordo della merce. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 7 caratteri.*/
    PesoNetto # peso netto della merce. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 7 caratteri.*/
    DataOraRitiro # data e ora del ritiro della merce (espressa secondo il formato ISO 8601:2004). la data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD-HH:MM*/
    DataInizioTrasporto # data di inizio del trasporto (espressa secondo il formato ISO 8601:2004). la data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD-HH:MM*/
    TipoResa # codice che identifica la tipologia di resa. codifica del termine di resa (Incoterms) espresso secondo lo standard ICC-Camera di Commercio Internazionale (formato alfanumerico di 3 caratteri)*/
    IndirizzoResa # si compone degli stessi campi previsti per l’elemento Sede*/
    DataOraConsegna # la data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD-HH:MM.*/

class DatiAnagraficiVettore: # Stessi campi di DatiAnagrafici, unificare se possibile
    IdFiscaleIVA IdFiscaleIVA;
    CodiceFiscale # numero di codice fiscale del cedente/prestatore. formato alfanumerico; lunghezza compresa tra  11 e 16 caratter*/
    Anagrafica
    AlboProfessionale #nome dell'albo professionale cui appartiene il  cedente/prestatore. formato alfanumerico; lunghezza massima  di 60 caratteri.*/
    ProvinciaAlbo # provincia dell'albo professionale. formato alfanumerico; lunghezza di 2 caratteri.  */
    NumeroIscrizioneAlbo #numero di iscrizione all'albo professionale. formato alfanumerico; lunghezza  massima di 60 caratter*/
    DataIscrizioneAlbo #data di iscrizione all'albo professionale (espressa secondo  il formato ISO 8601:2004). formato alfanumerico; lunghezza  massima di 60 caratter*/
    RegimeFiscale #Stesso discorso per DatiAnagrafici ... specificare i codici

class IndirizzoResa: #Stessi campi di Sede
    Indirizzo #indirizzo del cedente/prestatore del bene/servizio; deve essere  valorizzato con il nome della via, piazza, etc., comprensivo, se si vuole, del  numero civico formato alfanumerico; lunghezza  massima di 60 caratter*/
    NumeroCivico # numero civico relativo all’indirizzo specificato nel campo  precedente; si può omettere se già riportato nel campo precedente. formato alfanumerico; lunghezza massima di  8 caratteri.*/
    CAP #Codice di Avviamento Postale relativo all’indirizzo.formato numerico; lunghezza di 5 caratteri.  */
    Comune # Comune cui si riferisce l'indirizzo formato alfanumerico; lunghezza massima di 60  caratteri.*/
    Provincia # sigla della provincia di appartenenza del comune. formato alfanumerico; lunghezza di 2 caratteri.  */
    Nazione # codice della nazione espresso secondo lo standard ISO 3166-1  alpha-2 code sigla della nazione espressa secondo lo standard  ISO 3166-1 alpha-2 code.  */

class FatturaPrincipale:
    NumeroFatturaPrincipale # NumeroFatturaPrincipale: numero della fattura relativa al trasporto di beni, da  indicare sulle fatture emesse dagli autotrasportatori per certificare le operazioni  accessorie. formato alfanumerico; lunghezza  massima di 20 caratteri.  */
    DataFatturaPrincipale # DataFatturaPrincipale: data della fattura principale (espressa secondo il formato ISO 8601:2004). formato alfanumerico; lunghezza massima di 20 caratteri.*/

class DatiBeniServizi:
    DettaglioLinee
    DatiRiepilogo

class DettaglioLinee:
    NumeroLinea #numero che identifica la linea di dettaglio del bene/servizio riportata sul documento. formato numerico; lunghezza massima di 4 caratteri.*/
    TipoCessionePrestazione # codice che identifica la tipologia di cessione/prestazione qualora si tratti di sconto, premio, abbuono o spesa accessoria; è quindi valorizzabile soltanto in presenza di questi casi
    """ 
        formato alfanumerico; lunghezza di 2 caratteri; i ivalori ammessi sono:
		SC Sconto
		PR Premio
		AB Abbuono
		AC Spesa accessoria
	"""
    CodiceArticolo
    Descrizione # natura e qualità del bene/servizio oggetto della cessione/prestazione; può fare anche riferimento ad un precedente documento emesso a titolo di anticipo/acconto formato alfanumerico; lunghezza massima di 100 caratteri.*/
    Quantita # numero di unità cedute/prestate; può non essere valorizzato nei casi in cui la prestazione non sia quantificabile. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 21 caratteri.*/
    UnitaMisura # unità di misura in cui è espresso il campo Quantità. formato alfanumerico; lunghezza massima di 10 caratteri.*/
    DataInizioPeriodo # data iniziale del periodo di riferimento cui si riferisce l'eventuale servizio prestato (espressa secondo il formato ISO 8601:2004). formato alfanumerico; lunghezza massima di 10 caratteri.*/
    DataFinePeriodo # DataFinePeriodo: data finale del periodo di riferimento cui si riferisce l'eventuale servizio prestato (espressa secondo il formato ISO 8601:2004). formato alfanumerico; lunghezza massima di 10 caratteri..*/
    PrezzoUnitario # prezzo unitario del bene/servizio; nel caso di beni ceduti a titolo di sconto, premio o abbuono, l'importo indicato rappresenta il "valore normale”. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 21 caratteri.*/
    ScontoMaggiorazione
    PrezzoTotale #prezzo unitario del bene/servizio; nel caso di beni ceduti a titolo di sconto, premio o abbuono, l'importo indicato rappresenta il "valore normale”. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 21 caratter*/
    AliquotaIVA  #IVA (espressa in percentuale %) applicata alla cessione/prestazione; nel caso di non applicabilità, il campo deve essere valorizzato a zero.: formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 6 caratteri.*/
    Ritenuta # indica se la linea della fattura si riferisce ad una cessione/prestazione soggetta a ritenuta. formato alfanumerico; lunghezza di 2 caratteri; il valore ammesso è: SI linea di fattura soggetta a ritenuta*/
    Natura

	"""
    	codice che esprime la natura delle operazioni che non rientrano tra quelle imponibili.
		formato alfanumerico; lunghezza di 2 caratteri; i valori ammessi sono i seguenti:
		N1 escluse ex art.15
		N2 non soggette
		N3 non imponibili
		N4 esenti
		N5 regime del margine
	"""
    RiferimentoAmministrazione # eventuale riferimento utile all’aministrazione destinataria (capitolo di spesa, conto economico …). formato alfanumerico; lunghezza massima di 20 caratteri..*/
    AltriDatiGestionali

class CodiceArticolo:
    CodiceTipo # indica la tipologia di codice articolo (i.e.: TARIC, CPV, EAN, SSC, ...). formato alfanumerico; lunghezza massima di 35 caratteri.*/
    CodiceValore # valore del codice articolo corrispondente alla tipologia. formato alfanumerico; lunghezza massima di 35 caratteri.*/

class ScontoMaggiorazione:
	Tipo #indica se si tratta di sconto o di maggiorazione .
	"""
		formato alfanumerico; lunghezza di 2 caratteri; i valori ammessi sono i seguenti:
		SC sconto
		MG maggiorazione
	"""
    Percentuale #percentuale di sconto o di maggiorazione. formato numerico nel quale i decimali vanno separati dall’intero con il carattere ‘.’ (punto). La sua lunghezza va da 4 a 6 caratteri*/
    Importo #importo dello sconto o della maggiorazione. formato numerico nel quale i decimali vanno separati dall’intero con il carattere ‘.’ (punto). La sua lunghezza va da 4 a 15 caratteri.*/

class AltriDatiGestionali:
	TipoDato #codice che identifica la tipologia di informazione. formato alfanumerico; lunghezza massima di 10 caratteri.*/
    RiferimentoTesto #valore alfanumerico riferito alla tipologia di informazione. formato alfanumerico; lunghezza massima di 60 caratteri*/
    RiferimentoNumero #valore numerico riferito alla tipologia di informazione. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 21 caratteri.*/
    RiferimentoData #data riferita alla tipologia di informazione. La data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/

class DatiRiepilogo:
	AliquotaIVA #IVA (espressa in percentuale %) : formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 6 caratteri.*/
    Natura
    """
    	codice che esprime la natura delle operazioni che non rientrano tra quelle imponibili.
		formato alfanumerico; lunghezza di 2 caratteri; i valori ammessi sono i seguenti:
		N1 escluse ex art.15
		N2 non soggette
		N3 non imponibili
		N4 esenti
		N5 regime del margine
	"""
    SpeseAccessorie #corrispettivi relativi alle cessioni accessorie, (es. imballaggi etc.) qualora presenti. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    Arrotondamento; #arrotondamento sull'imponibile o sull’importo, qualora presente formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 21 caratteri.*/
    ImponibileImporto #valore che rappresenta la base imponibile, per le operazioni soggette ad IVA, oppure l’importo per le operazioni che non rientrano tra quelle 'imponibili'. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    Imposta # imposta corrispondente all’applicazione dell’aliquota IVA sul relativo imponibile. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    EsigibilitaIVA
    """
    	codice che esprime il regime di esigibilità dell’IVA (differita o immediata).
		formato alfanumerico; lunghezza di 1 carattere; i valori ammessi sono i seguenti
		D IVA ad esigibilità differita
		I IVA ad esigibilità immediata
	"""
    RiferimentoNormativo #normativa di riferimento (obbligatorio nei casi di operazioni di cui al campo Natura). formato alfanumerico; lunghezza massima di 100 caratteri.

class DatiVeicoli:
	Data #data di prima immatricolazione o di iscrizione del mezzo di trasporto nei pubblici registri (espressa secondo il formato ISO 8601:2004).*/
	TotalePercorso #totale chilometri percorsi, oppure totale ore navigate o volate del mezzo di trasporto.*/

class DatiPagamento:
    CondizioniPagamento 
    """
    	codice che identifica le condizioni di pagamento.
		formato alfanumerico; lunghezza di 4 caratteri; i valori ammessi sono i seguenti:
		TP01 pagamento a rate
		TP02 pagamento completo
		TP03 anticipo
	"""

    DettaglioPagamento

class DettaglioPagamento:
    Beneficiario #estremi anagrafici del beneficiario del pagamento (utilizzabile se si intende indicare un beneficiario diverso dal cedente/prestatore). formato alfanumerico; lunghezza massima di 200 caratteri.*/
    ModalitaPagamento
    """
    	codice che identifica le modalità di pagamento.
		formato alfanumerico; lunghezza di 4 caratteri; i valori ammessi sono i seguenti:
		MP01 contanti
		MP02 assegno
		MP03 assegno circolare
		MP04 contanti presso Tesoreria
		MP05 bonifico
		MP06 vaglia cambiario
		MP07 bollettino bancario
		MP08 carta di credito
		MP09 RID
		MP10 RID utenze
		MP11 RID veloce
		MP12 Riba
		MP13 MAV
		MP14 quietanza erario stato
		MP15 giroconto su conti di contabilità speciale
		MP16 domiciliazione bancaria
		MP17 domiciliazione postale
	"""
    DataRiferimentoTerminiPagamento # data dalla quale decorrono i termini di pagamento (espressa secondo il formato ISO 8601:2004). la data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    GiorniTerminiPagamento #ermine di pagamento espresso in giorni a partire dalla data di riferimento di cui al campo DataRiferimentoTerminiPagamento. formato numerico di lunghezza massima pari a 3. Vale 0 (zero) per pagamenti a vista.*/
    DataScadenzaPagamento # data di scadenza del pagamento (espressa secondo il formato ISO 8601:2004). la data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    ImportoPagamento #importo relativo al pagamento. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    CodUfficioPostale # /*codice dell’ufficio postale (nei casi di modalità di pagamento che ne presuppongono l’indicazione). formato alfanumerico; lunghezza massima di 20 caratteri.*/
    CognomeQuietanzante # /*cognome del quietanzante, nei casi di modalità di pagamento di “contanti presso tesoreria”. formato alfanumerico; lunghezza massima di 60 caratteri.*/
    NomeQuietanzante #nome del quietanzante, nei casi di modalità di pagamento di “contanti presso tesoreria”. formato alfanumerico; lunghezza massima di 60 caratteri.*/
    CFQuietanzante #codice fiscale del quietanzante nei casi di modalità di pagamento di “contanti presso tesoreria”. : formato alfanumerico; lunghezza di 16 caratteri.*/
    TitoloQuietanzante #titolo del quietanzante nei casi di modalità di pagamento di “contanti presso tesoreria”. formato alfanumerico; lunghezza che va da 2 a 10 caratteri.*/
    IstitutoFinanziario #nome dell'Istituto Finanziario presso il quale effettuare il pagamento. formato alfanumerico; lunghezza massima di 80 caratteri.*/
    IBAN #coordinata bancaria internazionale che consente di identificare, in maniera standard, il conto corrente del beneficiario (International Bank Account Number.) formato alfanumerico; lunghezza che va da 27 a 34 caratteri.*/
    ABI #codice ABI (Associazione Bancaria Italiana). formato numerico di 5 caratteri.*/
    CAB #codice CAB (Codice di Avviamento Bancario). formato numerico di 5 caratteri.*/
    BIC #codice BIC (Bank Identifier Code).formato alfanumerico; lunghezza che va da 8 a 11 caratteri.*/
    ScontoPagamentoAnticipato #ammontare dello sconto per pagamento anticipato.formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    DataLimitePagamentoAnticipato # data limite stabilita per il pagamento anticipato (espressa secondo il formato ISO 8601:2004). formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    PenalitaPagamentiRitardati # ammontare della penalità dovuta per pagamenti ritardati. formato numerico nel quale i decimali vanno separati dall'intero con il carattere '.' (punto). La sua lunghezza va da 4 a 15 caratteri.*/
    DataDecorrenzaPenale #data di decorrenza della penale (espressa secondo il formato ISO 8601:2004) : la data deve essere rappresentata secondo il formato ISO 8601:2004, con la seguente precisione: YYYY-MM-DD.*/
    CodicePagamento #codice da utilizzare per la riconciliazione degli incassi da parte del cedente/prestatore. formato alfanumerico; lunghezza massima di 15 caratteri.*/

class Allegati
    NomeAttachment #contiene il nome del documento allegato alla fattura elettronica*/
    AlgoritmoCompressione #algoritmo utilizzato per comprimere l’allegato.*/
    FormatoAttachment #formato dell’allegato.*/
    DescrizioneAttachment #descrizione del documento allegato alla fattura elettronica.*/
    Attachment #contiene il documento allegato alla fattura elettronica.