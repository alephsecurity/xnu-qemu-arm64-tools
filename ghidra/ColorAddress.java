import java.awt.Color;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;

public class ColorAddress  extends GhidraScript {
	private static final Logger LOGGER = Logger.getLogger(ColorAddress.class.getName());
	@Override
	protected void run() throws Exception {
		LOGGER.setLevel(Level.WARNING);
		
		List<Address> listOfInstPtrToCollor = getAddresses();
		AddressSet addresses = new AddressSet();
		Address minAddress = currentProgram.getMinAddress();
		Address maxAddress = currentProgram.getMaxAddress();
		int counter = 0;
		if(listOfInstPtrToCollor == null) {
			LOGGER.warning("List is null!");
			return;
		}
		for (Address addr : listOfInstPtrToCollor) {
			//Check whether we are in the correct adress space
			if (addr.compareTo(minAddress)>=0 && addr.compareTo(maxAddress) <=0){
				addresses.add(addr);
				counter++;
			}
		}

		//pink fuchsia <3
		setBackgroundColor(addresses, new Color(255, 119, 255));
		LOGGER.info(String.format("%d pointers were colored!",counter));
	}
	
	private List<Address> getAddresses(){
		
		Pattern pattern = Pattern.compile("((Trace \\d: 0x.+? \\[.+?/)(.+)(/.+\\] ))");
		List<Address> lst = new ArrayList<Address>();
		BufferedReader reader;
		File file;
		String line ;
		try {
			file = askFile("TRACES of QEMU execution", "Choose file:");
			LOGGER.info("File chosen " + file);
			
			reader = new BufferedReader(new FileReader(file));
			line = reader.readLine();
			while (line != null) {
				Matcher m = pattern.matcher(line);
				if(m.matches() && m.groupCount() == 4) {
					lst.add(currentAddress.getAddress("0x" + m.group(3)));
					LOGGER.info("Adding address to be colored: 0x" + m.group(3));
				}
				line = reader.readLine();
			}
			reader.close();
			
		} catch (Exception e) {
			e.printStackTrace();
		}
		return lst;
	}

}
