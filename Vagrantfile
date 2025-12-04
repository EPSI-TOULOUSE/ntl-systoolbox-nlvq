Vagrant.configure("2") do |config|
  MACHINES = {
    ubuntu: {
      box: "generic/ubuntu2004",
      hostname: "ubuntu",
      ip: "192.168.1.10",
      memory: 2048,
      cpus: 2,
      winrm: false
    },
    windows: {
      box: "jborean93/WindowsServer2019",
      hostname: "windows",
      ip: "192.168.1.20",
      memory: 4096,
      cpus: 2,
      winrm: true
    }
  }

  config.vm.synced_folder ".", "/vagrant", disabled: true

  def setup_providers(vm, name, memory, cpus)

    # VirtualBox
    vm.provider "virtualbox" do |vb|
      vb.name   = name
      vb.memory = memory
      vb.cpus   = cpus
    end

    # Libvirt
    vm.provider "libvirt" do |lv|
      lv.memory = memory
      lv.cpus   = cpus
      lv.nic_model_type = "virtio"
      lv.video_type = "vga"
      lv.video_vram = 16384
    end

    # VMware
    vm.provider "vmware_desktop" do |vmw|
      vmw.vmx["displayName"] = name
      vmw.vmx["memsize"]  = memory.to_s
      vmw.vmx["numvcpus"] = cpus.to_s
    end
  end

  # Loop sur les machines
  MACHINES.each do |key, cfg|
    config.vm.define key.to_s do |vm|
      vm.vm.box = cfg[:box]
      vm.vm.hostname = cfg[:hostname]
      vm.vm.network "private_network", ip: cfg[:ip]
      vm.vm.communicator = "winrm" if cfg[:winrm]

      setup_providers(
        vm.vm,
        "ntl-#{cfg[:hostname]}",
        cfg[:memory],
        cfg[:cpus]
      )
    end
  end
end
